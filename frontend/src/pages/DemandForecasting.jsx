import React, { useState, useEffect } from 'react'
import { Box, Typography, Paper, Grid, Select, MenuItem, FormControl, InputLabel, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'

export default function DemandForecasting() {
  const [daysAhead, setDaysAhead] = useState(7)
  const [forecast, setForecast] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchForecast()
  }, [daysAhead])

  const fetchForecast = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/analytics/forecast?days_ahead=${daysAhead}`)
      
      // Convert to array if it's an object
      const forecastData = response.data.forecast
      const formattedData = Array.isArray(forecastData) 
        ? forecastData 
        : Object.values(forecastData)[0] // Get first stop's data
      
      setForecast(formattedData)
    } catch (error) {
      console.error('Error fetching forecast:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Demand Forecasting (Deep Learning)
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Forecast Period</InputLabel>
          <Select
            value={daysAhead}
            label="Forecast Period"
            onChange={(e) => setDaysAhead(e.target.value)}
          >
            <MenuItem value={3}>3 Days</MenuItem>
            <MenuItem value={7}>7 Days</MenuItem>
            <MenuItem value={14}>14 Days</MenuItem>
            <MenuItem value={30}>30 Days</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Predicted Student Demand
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={forecast}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="predicted_count" stroke="#1976d2" name="Predicted Students" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Forecast Details
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Day</TableCell>
                    <TableCell align="right">Predicted Count</TableCell>
                    <TableCell align="right">Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {forecast.map((row, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{row.date}</TableCell>
                      <TableCell>{row.day_of_week}</TableCell>
                      <TableCell align="right">{row.predicted_count}</TableCell>
                      <TableCell align="right">{(row.confidence * 100).toFixed(1)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Model Information
            </Typography>
            <Typography>Model Type: LSTM (Long Short-Term Memory)</Typography>
            <Typography>Features: Day of week, month, holidays, weather, temperature, historical patterns</Typography>
            <Typography>Training Data: 90 days historical ridership</Typography>
            <Typography>Update Frequency: Daily</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
