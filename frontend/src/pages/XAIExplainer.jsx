import React, { useState } from 'react'
import { Box, Typography, Paper, Grid, Button, Select, MenuItem, FormControl, InputLabel, Card, CardContent, Chip } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'

export default function XAIExplainer() {
  const [method, setMethod] = useState('shap')
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleExplain = async () => {
    setLoading(true)
    try {
      const response = await axios.post('/api/xai/explain/optimization', {
        optimization_id: 1,
        method: method
      })
      setExplanation(response.data.explanation)
    } catch (error) {
      console.error('Error generating explanation:', error)
    } finally {
      setLoading(false)
    }
  }

  const getFeatureImportance = async () => {
    try {
      const response = await axios.get('/api/xai/feature-importance?model=genetic')
      const data = Object.entries(response.data.features).map(([name, value]) => ({
        name,
        importance: value
      }))
      
      setExplanation({
        method: 'feature_importance',
        features: data
      })
    } catch (error) {
      console.error('Error getting feature importance:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Explainable AI (XAI)
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate Explanation
        </Typography>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Explanation Method</InputLabel>
              <Select
                value={method}
                label="Explanation Method"
                onChange={(e) => setMethod(e.target.value)}
              >
                <MenuItem value="shap">SHAP (SHapley Additive exPlanations)</MenuItem>
                <MenuItem value="lime">LIME (Local Interpretable Model-agnostic)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" onClick={handleExplain} disabled={loading}>
            Explain Route Decision
          </Button>
          <Button variant="outlined" onClick={getFeatureImportance}>
            Show Feature Importance
          </Button>
        </Box>
      </Paper>

      {explanation && (
        <>
          {explanation.method === 'feature_importance' && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Feature Importance
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={explanation.features}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="importance" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          )}

          {(explanation.shap_values || explanation.local_explanation) && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    {method.toUpperCase()} Explanation
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Method: {explanation.method}
                  </Typography>
                  {explanation.prediction && (
                    <Typography gutterBottom>
                      Prediction Score: {explanation.prediction.toFixed(3)}
                    </Typography>
                  )}
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Feature Contributions
                  </Typography>
                  <Grid container spacing={2}>
                    {(explanation.shap_values || explanation.local_explanation || []).slice(0, 5).map((item, idx) => (
                      <Grid item xs={12} sm={6} md={4} key={idx}>
                        <Card>
                          <CardContent>
                            <Typography variant="subtitle1" gutterBottom>
                              {item.feature}
                            </Typography>
                            <Typography variant="h6">
                              {item.value?.toFixed(2) || 'N/A'}
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                              <Chip 
                                label={item.impact || (item.weight > 0 ? 'positive' : 'negative')}
                                color={item.impact === 'positive' || item.weight > 0 ? 'success' : 'error'}
                                size="small"
                              />
                            </Box>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              Impact: {Math.abs(item.shap_value || item.weight || 0).toFixed(3)}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Interpretation
                  </Typography>
                  <Typography paragraph>
                    The chart above shows how each feature contributed to the routing decision.
                  </Typography>
                  <Typography paragraph>
                    <strong>Positive impact</strong> means the feature increased the optimization score.
                  </Typography>
                  <Typography paragraph>
                    <strong>Negative impact</strong> means the feature decreased the optimization score.
                  </Typography>
                  <Typography>
                    This helps administrators understand <em>why</em> certain routes were chosen and make informed decisions.
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          )}
        </>
      )}
    </Box>
  )
}
