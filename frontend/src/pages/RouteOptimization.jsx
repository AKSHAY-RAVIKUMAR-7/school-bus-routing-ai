import React, { useState } from 'react'
import { Box, Typography, Paper, Button, TextField, Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert } from '@mui/material'
import axios from 'axios'

export default function RouteOptimization() {
  const [algorithm, setAlgorithm] = useState('genetic')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleOptimize = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Sample data for optimization
      const requestData = {
        algorithm: algorithm,
        stops: [
          { id: 1, location: { lat: 40.7128, lng: -74.0060 }, students: 5 },
          { id: 2, location: { lat: 40.7580, lng: -73.9855 }, students: 8 },
          { id: 3, location: { lat: 40.7489, lng: -73.9680 }, students: 6 },
          { id: 4, location: { lat: 40.7614, lng: -73.9776 }, students: 7 },
          { id: 5, location: { lat: 40.7306, lng: -73.9352 }, students: 4 }
        ],
        buses: [
          { id: 1, capacity: 50 },
          { id: 2, capacity: 45 }
        ],
        constraints: {
          max_time: 60,
          max_distance: 50
        }
      }

      const response = await axios.post('/api/routes/optimize', requestData)
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Optimization failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Route Optimization
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configure Optimization
        </Typography>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Algorithm</InputLabel>
          <Select
            value={algorithm}
            label="Algorithm"
            onChange={(e) => setAlgorithm(e.target.value)}
          >
            <MenuItem value="genetic">Genetic Algorithm</MenuItem>
            <MenuItem value="rl">Reinforcement Learning</MenuItem>
            <MenuItem value="hybrid">Hybrid (GA + RL)</MenuItem>
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          onClick={handleOptimize}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Optimize Routes'}
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Optimization Results
          </Typography>
          
          <Typography variant="body1" gutterBottom>
            Algorithm: <strong>{result.algorithm}</strong>
          </Typography>
          
          <Typography variant="h6" sx={{ mt: 2 }}>
            Metrics:
          </Typography>
          <ul>
            <li>Total Distance: {result.metrics.total_distance_km} km</li>
            <li>Estimated Time: {result.metrics.estimated_time_minutes} minutes</li>
            <li>Stops: {result.metrics.stops_count}</li>
            {result.metrics.fuel_consumption_liters && (
              <li>Fuel Consumption: {result.metrics.fuel_consumption_liters} liters</li>
            )}
          </ul>

          <Typography variant="h6" sx={{ mt: 2 }}>
            Routes: {result.routes.length}
          </Typography>
          {result.routes.map((route, idx) => (
            <Box key={idx} sx={{ mt: 1, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              <Typography>
                Bus {route.bus_id}: {route.stops.length} stops
              </Typography>
            </Box>
          ))}
        </Paper>
      )}
    </Box>
  )
}
