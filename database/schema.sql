-- School Bus Routing System Database Schema

-- Create database
CREATE DATABASE school_bus;

-- Connect to database
\c school_bus;

-- Buses table
CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    bus_number VARCHAR(20) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL,
    fuel_efficiency FLOAT,
    status VARCHAR(20) DEFAULT 'active',
    current_location JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(10),
    home_address VARCHAR(255),
    home_location JSONB,
    parent_contact VARCHAR(20),
    parent_email VARCHAR(100),
    assigned_stop_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stops table
CREATE TABLE stops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location JSONB NOT NULL,
    address VARCHAR(255),
    pickup_time TIMESTAMP,
    dropoff_time TIMESTAMP,
    student_count INTEGER DEFAULT 0,
    geofence_radius FLOAT DEFAULT 100
);

-- Routes table
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bus_id INTEGER REFERENCES buses(id),
    route_type VARCHAR(20),
    total_distance FLOAT,
    estimated_duration INTEGER,
    optimization_score FLOAT,
    ai_metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route stops junction table
CREATE TABLE route_stops (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES routes(id) ON DELETE CASCADE,
    stop_id INTEGER REFERENCES stops(id),
    sequence INTEGER NOT NULL,
    arrival_time TIMESTAMP,
    departure_time TIMESTAMP,
    distance_from_previous FLOAT
);

-- Tracking data table
CREATE TABLE tracking_data (
    id SERIAL PRIMARY KEY,
    bus_id INTEGER REFERENCES buses(id),
    location JSONB NOT NULL,
    speed FLOAT,
    heading FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accuracy FLOAT
);

-- Demand forecasts table
CREATE TABLE demand_forecasts (
    id SERIAL PRIMARY KEY,
    stop_id INTEGER REFERENCES stops(id),
    forecast_date TIMESTAMP NOT NULL,
    predicted_count INTEGER,
    confidence FLOAT,
    model_version VARCHAR(20),
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimization history table
CREATE TABLE optimization_history (
    id SERIAL PRIMARY KEY,
    algorithm VARCHAR(50),
    input_params JSONB,
    output_routes JSONB,
    metrics JSONB,
    execution_time FLOAT,
    xai_explanation JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_buses_status ON buses(status);
CREATE INDEX idx_students_active ON students(is_active);
CREATE INDEX idx_routes_active ON routes(is_active);
CREATE INDEX idx_tracking_bus_time ON tracking_data(bus_id, timestamp DESC);
CREATE INDEX idx_route_stops_route ON route_stops(route_id);

-- Add foreign key constraint
ALTER TABLE students ADD CONSTRAINT fk_students_stop 
    FOREIGN KEY (assigned_stop_id) REFERENCES stops(id);

-- Insert sample data
INSERT INTO buses (bus_number, capacity, fuel_efficiency, status) VALUES
('BUS-001', 50, 8.5, 'active'),
('BUS-002', 45, 9.0, 'active'),
('BUS-003', 55, 8.0, 'active');

INSERT INTO stops (name, location, address, student_count) VALUES
('Stop 1 - Main Street', '{"lat": 40.7128, "lng": -74.0060}', '123 Main St', 12),
('Stop 2 - Oak Avenue', '{"lat": 40.7580, "lng": -73.9855}', '456 Oak Ave', 15),
('Stop 3 - Pine Road', '{"lat": 40.7489, "lng": -73.9680}', '789 Pine Rd', 10),
('Stop 4 - Elm Street', '{"lat": 40.7614, "lng": -73.9776}', '321 Elm St', 18),
('Stop 5 - Maple Drive', '{"lat": 40.7306, "lng": -73.9352}', '654 Maple Dr', 8);

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
