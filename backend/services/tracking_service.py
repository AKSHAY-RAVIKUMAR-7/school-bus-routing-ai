"""
Real-time Tracking Service

Handles GPS location updates, geofencing, and real-time notifications
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.connection import get_db, redis_client
from database.models import Bus, TrackingData
import json
import logging

logger = logging.getLogger(__name__)

class TrackingService:
    """Service for managing real-time bus tracking"""
    
    def __init__(self):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour
        self.memory_cache = {}  # Fallback cache
    
    def update_location(self, bus_id: int, location: Dict[str, float],
                       speed: Optional[float] = None,
                       heading: Optional[float] = None,
                       accuracy: float = 10.0) -> Dict:
        """
        Update bus location
        
        Args:
            bus_id: Bus ID
            location: {"lat": float, "lng": float}
            speed: Speed in km/h
            heading: Heading in degrees (0-360)
            accuracy: GPS accuracy in meters
        
        Returns:
            Updated tracking info
        """
        try:
            db = next(get_db())
            
            # Create tracking record
            tracking = TrackingData(
                bus_id=bus_id,
                location=location,
                speed=speed,
                heading=heading,
                accuracy=accuracy,
                timestamp=datetime.utcnow()
            )
            
            db.add(tracking)
            db.commit()
            
            # Update Redis cache for fast access
            cache_key = f"bus_location:{bus_id}"
            cache_data = {
                'location': location,
                'speed': speed,
                'heading': heading,
                'timestamp': tracking.timestamp.isoformat(),
                'accuracy': accuracy
            }
            
            if self.redis:
                self.redis.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(cache_data)
                )
            else:
                self.memory_cache[cache_key] = cache_data
            
            # Check geofences
            self._check_geofences(bus_id, location)
            
            logger.info(f"Updated location for bus {bus_id}: {location}")
            
            return {
                'success': True,
                'timestamp': tracking.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating location: {str(e)}")
            raise
    
    def get_current_location(self, bus_id: int) -> Optional[Dict]:
        """
        Get current location of a bus
        First checks Redis cache, then database
        """
        try:
            # Check cache first
            cache_key = f"bus_location:{bus_id}"
            
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            elif cache_key in self.memory_cache:
                return self.memory_cache[cache_key]
            
            # Fallback to database
            db = next(get_db())
            tracking = db.query(TrackingData)\
                        .filter(TrackingData.bus_id == bus_id)\
                        .order_by(TrackingData.timestamp.desc())\
                        .first()
            
            if tracking:
                data = {
                    'location': tracking.location,
                    'speed': tracking.speed,
                    'heading': tracking.heading,
                    'timestamp': tracking.timestamp.isoformat(),
                    'accuracy': tracking.accuracy
                }
                
                # Update cache
                if self.redis:
                    self.redis.setex(cache_key, self.cache_ttl, json.dumps(data))
                else:
                    self.memory_cache[cache_key] = data
                
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting location: {str(e)}")
            return None
    
    def get_history(self, bus_id: int, start_time: Optional[str] = None,
                   end_time: Optional[str] = None) -> List[Dict]:
        """Get historical tracking data for a bus"""
        try:
            db = next(get_db())
            
            query = db.query(TrackingData).filter(TrackingData.bus_id == bus_id)
            
            if start_time:
                query = query.filter(TrackingData.timestamp >= datetime.fromisoformat(start_time))
            
            if end_time:
                query = query.filter(TrackingData.timestamp <= datetime.fromisoformat(end_time))
            
            tracking_data = query.order_by(TrackingData.timestamp.asc()).all()
            
            return [
                {
                    'location': t.location,
                    'speed': t.speed,
                    'heading': t.heading,
                    'timestamp': t.timestamp.isoformat(),
                    'accuracy': t.accuracy
                }
                for t in tracking_data
            ]
            
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
    
    def _check_geofences(self, bus_id: int, location: Dict[str, float]):
        """
        Check if bus has entered/exited any geofences (stops)
        Trigger notifications if needed
        """
        try:
            from database.models import Stop
            
            db = next(get_db())
            stops = db.query(Stop).all()
            
            for stop in stops:
                distance = self._calculate_distance(
                    location,
                    stop.location
                )
                
                # Check if within geofence
                if distance <= stop.geofence_radius:
                    logger.info(f"Bus {bus_id} entered geofence of stop {stop.id}")
                    self._trigger_geofence_event(bus_id, stop.id, 'entered')
                
        except Exception as e:
            logger.error(f"Error checking geofences: {str(e)}")
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two points in meters using Haversine"""
        import math
        
        lat1, lon1 = math.radians(loc1['lat']), math.radians(loc1['lng'])
        lat2, lon2 = math.radians(loc2['lat']), math.radians(loc2['lng'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371000 * c  # Earth radius in meters
    
    def _trigger_geofence_event(self, bus_id: int, stop_id: int, event_type: str):
        """Trigger geofence event (send notifications)"""
        # Publish to Redis pub/sub for notifications
        event = {
            'bus_id': bus_id,
            'stop_id': stop_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if self.redis:
            self.redis.publish('geofence_events', json.dumps(event))
        logger.info(f"Geofence event published: {event}")
