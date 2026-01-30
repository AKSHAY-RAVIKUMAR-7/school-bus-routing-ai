import React, { useState, useEffect } from 'react'
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus'
import RouteIcon from '@mui/icons-material/Route'
import PeopleIcon from '@mui/icons-material/People'
import SpeedIcon from '@mui/icons-material/Speed'
import axios from 'axios'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_buses: 0,
    active_routes: 0,
    total_students: 0,
    avg_efficiency: 0
  })

  const [chartData, setChartData] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/analytics/dashboard')
      const data = response.data.dashboard
      
      setStats({
        total_buses: data.total_buses,
        active_routes: data.active_routes,
        total_students: data.total_students,
        avg_efficiency: data.avg_efficiency
      })

      // Mock chart data
      setChartData([
        { name: 'Mon', efficiency: 85, distance: 450 },
        { name: 'Tue', efficiency: 88, distance: 420 },
        { name: 'Wed', efficiency: 82, distance: 480 },
        { name: 'Thu', efficiency: 90, distance: 410 },
        { name: 'Fri', efficiency: 87, distance: 440 },
      ])
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
  }

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 48 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Buses"
            value={stats.total_buses}
            icon={<DirectionsBusIcon fontSize="inherit" />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Routes"
            value={stats.active_routes}
            icon={<RouteIcon fontSize="inherit" />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Students"
            value={stats.total_students}
            icon={<PeopleIcon fontSize="inherit" />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Efficiency"
            value={`${stats.avg_efficiency}%`}
            icon={<SpeedIcon fontSize="inherit" />}
            color="#9c27b0"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Weekly Efficiency
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="efficiency" stroke="#1976d2" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Distance Traveled (km)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="distance" fill="#2e7d32" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
