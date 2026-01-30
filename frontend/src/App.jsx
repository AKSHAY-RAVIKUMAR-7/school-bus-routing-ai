import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RealTimeTracking from './pages/RealTimeTracking'
import RouteOptimization from './pages/RouteOptimization'
import Analytics from './pages/Analytics'
import DemandForecasting from './pages/DemandForecasting'
import XAIExplainer from './pages/XAIExplainer'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tracking" element={<RealTimeTracking />} />
            <Route path="/optimize" element={<RouteOptimization />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/forecast" element={<DemandForecasting />} />
            <Route path="/xai" element={<XAIExplainer />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App
