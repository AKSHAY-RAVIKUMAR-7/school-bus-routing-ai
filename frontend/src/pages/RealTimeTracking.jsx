import React, { useState, useEffect } from 'react'
import { Box, Typography, Paper } from '@mui/material'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import { io } from 'socket.io-client'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'

export default function RealTimeTracking() {
  const [buses, setBuses] = useState([])
  const [socket, setSocket] = useState(null)

  useEffect(() => {
    // Fetch initial bus locations
    fetchBuses()

    // Setup WebSocket connection
    const newSocket = io('http://localhost:5000/tracking')
    setSocket(newSocket)

    newSocket.on('location_update', (data) => {
      updateBusLocation(data)
    })

    return () => newSocket.close()
  }, [])

  const fetchBuses = async () => {
    try {
      const response = await axios.get('/api/tracking/buses/active')
      setBuses(response.data.buses)
    } catch (error) {
      console.error('Error fetching buses:', error)
    }
  }

  const updateBusLocation = (data) => {
    setBuses(prevBuses => 
      prevBuses.map(bus => 
        bus.id === data.bus_id 
          ? { ...bus, location: data.location, speed: data.speed }
          : bus
      )
    )
  }

  const centerPosition = [40.7128, -74.0060] // Default to NYC

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Real-Time Bus Tracking
      </Typography>

      <Paper sx={{ height: 'calc(100vh - 200px)', p: 2 }}>
        <MapContainer 
          center={centerPosition} 
          zoom={13} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {buses.map(bus => (
            bus.location && (
              <Marker 
                key={bus.id} 
                position={[bus.location.lat, bus.location.lng]}
              >
                <Popup>
                  <div>
                    <strong>Bus {bus.bus_number}</strong><br />
                    Speed: {bus.speed ? `${bus.speed.toFixed(1)} km/h` : 'N/A'}<br />
                    Last Update: {bus.last_update}
                  </div>
                </Popup>
              </Marker>
            )
          ))}
        </MapContainer>
      </Paper>
    </Box>
  )
}
