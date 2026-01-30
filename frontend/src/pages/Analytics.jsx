import React, { useState, useEffect } from 'react'
import { Box, Typography, Paper, Grid } from '@mui/material'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

export default function Analytics() {
  const [efficiency, setEfficiency] = useState(null)
  const [fuelData, setFuelData] = useState(null)
  const [delayData, setDelayData] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [efficiencyRes, fuelRes, delayRes] = await Promise.all([
        axios.get('/api/analytics/efficiency?period=week'),
        axios.get('/api/analytics/fuel-consumption?period=month'),
        axios.get('/api/analytics/delays')
      ])

      setEfficiency(efficiencyRes.data.metrics)
      setFuelData(fuelRes.data.consumption)
      setDelayData(delayRes.data.analysis)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics & Insights
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Route Efficiency Metrics
            </Typography>
            {efficiency && (
              <Box>
                <Typography>Average Distance: {efficiency.average_distance} km</Typography>
                <Typography>Average Time: {efficiency.average_time} minutes</Typography>
                <Typography>Efficiency Score: {efficiency.average_efficiency_score}</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Fuel Consumption
            </Typography>
            {fuelData && (
              <Box>
                <Typography>Total Distance: {fuelData.total_distance_km} km</Typography>
                <Typography>Total Fuel: {fuelData.total_fuel_liters} liters</Typography>
                <Typography>Estimated Cost: ${fuelData.estimated_cost}</Typography>
                <Typography>Average Efficiency: {fuelData.average_efficiency} km/l</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Delay Analysis
            </Typography>
            {delayData && (
              <Box>
                <Typography>Average Delay: {delayData.average_delay_minutes} minutes</Typography>
                <Typography>Delay Frequency: {(delayData.delay_frequency * 100).toFixed(1)}%</Typography>
                <Typography>Predicted Tomorrow: {delayData.predicted_delay_tomorrow} minutes</Typography>
                
                <ResponsiveContainer width="100%" height={200} style={{ marginTop: 20 }}>
                  <PieChart>
                    <Pie
                      data={delayData.common_causes}
                      dataKey="percentage"
                      nameKey="cause"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {delayData.common_causes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            {delayData && (
              <ul>
                {delayData.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
