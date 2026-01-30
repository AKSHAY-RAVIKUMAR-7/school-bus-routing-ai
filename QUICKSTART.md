# 🚀 Quick Start Guide

## Prerequisites

Ensure you have the following installed:
- Python 3.9+ ([Download](https://www.python.org/downloads/))
- Node.js 16+ ([Download](https://nodejs.org/))
- PostgreSQL 13+ ([Download](https://www.postgresql.org/download/))
- Redis 6+ ([Download](https://redis.io/download))
- Git

## Installation Steps

### 1. Clone the Repository (if applicable)

```bash
git clone https://github.com/your-username/school-bus-routing.git
cd school-bus-routing
```

### 2. Set Up Database

#### Windows:
```powershell
# Start PostgreSQL service
# Open psql and run:
psql -U postgres -f database/schema.sql
```

#### Linux/Mac:
```bash
sudo service postgresql start
psql -U postgres -f database/schema.sql
```

### 3. Set Up Redis

#### Windows:
Download and install Redis from [GitHub](https://github.com/microsoftarchive/redis/releases)

#### Linux/Mac:
```bash
sudo service redis-server start
```

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file with your configurations

# Initialize database
python -c "from database.connection import init_db; init_db()"

# Run the application
python app.py
```

Backend will be available at: http://localhost:5000

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🐳 Docker Setup (Alternative)

If you prefer Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📱 Features Overview

### 1. Dashboard
- Real-time statistics
- System overview
- Performance metrics

### 2. Real-Time Tracking
- Live bus locations on map
- WebSocket updates
- Geofencing alerts

### 3. Route Optimization
- Genetic Algorithm optimization
- Reinforcement Learning
- Hybrid approach

### 4. Analytics
- Route efficiency metrics
- Fuel consumption analysis
- Delay predictions

### 5. Demand Forecasting
- LSTM-based predictions
- 7-30 day forecasts
- Confidence intervals

### 6. AI Explainer (XAI)
- SHAP explanations
- LIME interpretations
- Feature importance

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/school_bus
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
MQTT_BROKER=localhost
GOOGLE_MAPS_API_KEY=your-api-key
```

### API Endpoints

- Health Check: `GET http://localhost:5000/health`
- Route Optimization: `POST http://localhost:5000/api/routes/optimize`
- Bus Tracking: `GET http://localhost:5000/api/tracking/buses/active`
- Analytics: `GET http://localhost:5000/api/analytics/efficiency`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📊 Sample Data

The system includes sample data:
- 3 buses
- 5 stops
- Historical tracking data

To add more data, use the admin interface or API endpoints.

## 🚨 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists

### Redis Connection Error
- Ensure Redis is running
- Check REDIS_URL in .env

### Port Already in Use
- Backend (5000): Change in app.py
- Frontend (3000): Change in vite.config.js

### CORS Issues
- Check CORS configuration in app.py
- Verify frontend API proxy in vite.config.js

## 📚 Next Steps

1. Customize routes and stops for your organization
2. Configure Google Maps API for real routing
3. Set up MQTT broker for GPS devices
4. Train ML models with historical data
5. Configure notifications and alerts
6. Deploy to production environment

## 🤝 Support

For issues and questions:
- Create a GitHub issue
- Check documentation
- Contact: support@schoolbus.ai

## 📄 License

MIT License - See LICENSE file for details
