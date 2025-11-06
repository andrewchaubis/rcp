import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, FormControl, InputLabel, Select, MenuItem,
  Button, Slider, Chip, Alert, CircularProgress, Paper, Accordion, AccordionSummary,
  AccordionDetails, FormControlLabel, Checkbox, TextField
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Plot from 'react-plotly.js';
import { apiService } from '../services/api';

const QuickAnalysis = () => {
  const [locations, setLocations] = useState([]);
  const [dataSource, setDataSource] = useState('ISIMIP Historical Data');
  const [location, setLocation] = useState('Malaysia (Country)');
  const [region, setRegion] = useState('peninsular');
  const [years, setYears] = useState(30);
  const [timeWindow, setTimeWindow] = useState(365);
  const [eventTypes, setEventTypes] = useState(['flood', 'heavy_rainfall', 'extreme_rainfall']);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [probabilities, setProbabilities] = useState(null);
  const [seasonalData, setSeasonalData] = useState(null);
  const [rainfallTimeseries, setRainfallTimeseries] = useState(null);
  const [dischargeTimeseries, setDischargeTimeseries] = useState(null);
  const [trendPrediction, setTrendPrediction] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const response = await apiService.getLocations();
      setLocations(response.data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const handleDataGeneration = async () => {
    setLoading(true);
    try {
      const requestData = {
        data_source: dataSource,
        location: dataSource === 'ISIMIP Historical Data' ? location : undefined,
        region: dataSource === 'Generate Sample Data' ? region : undefined,
        years: years,
        time_window: timeWindow,
        event_types: eventTypes
      };

      const response = await apiService.generateData(requestData);
      setSessionId(response.data.session_id);
      setData(response.data);
      
      // Load time series data
      await loadTimeseriesData(response.data.session_id);
    } catch (error) {
      console.error('Error generating data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const response = await apiService.uploadData(file);
      const sessionIdFromResponse = response.data.message.match(/Session ID: (.+)/)[1];
      setSessionId(sessionIdFromResponse);
      setUploadedFile(file);
      setData({
        message: response.data.message,
        data_summary: {
          total_days: response.data.rows,
          columns: response.data.columns
        }
      });
      
      await loadTimeseriesData(sessionIdFromResponse);
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTimeseriesData = async (sessionId) => {
    try {
      const rainfallResponse = await apiService.getRainfallTimeseries(sessionId);
      setRainfallTimeseries(rainfallResponse.data);

      try {
        const dischargeResponse = await apiService.getDischargeTimeseries(sessionId);
        if (dischargeResponse.data.dates) {
          setDischargeTimeseries(dischargeResponse.data);
        }
      } catch (error) {
        // Discharge data might not be available for all data sources
        console.log('No discharge data available');
      }
    } catch (error) {
      console.error('Error loading timeseries data:', error);
    }
  };

  const handleProbabilityAnalysis = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      const requestData = {
        data_source: dataSource,
        time_window: timeWindow,
        event_types: eventTypes
      };

      const response = await apiService.analyzeProbabilities(sessionId, requestData);
      setProbabilities(response.data.probabilities);
      setSeasonalData(response.data.seasonal_analysis);
    } catch (error) {
      console.error('Error analyzing probabilities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendPrediction = async (eventType, yearsAhead) => {
    if (!sessionId) return;

    setLoading(true);
    try {
      const response = await apiService.predictTrend(sessionId, {
        event_type: eventType,
        years_ahead: yearsAhead
      });
      setTrendPrediction(response.data);
    } catch (error) {
      console.error('Error predicting trend:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEventTypeChange = (event) => {
    const value = event.target.value;
    setEventTypes(typeof value === 'string' ? value.split(',') : value);
  };

  const formatTimeWindow = (value) => {
    if (value >= 365) return `${value} days (${(value/365).toFixed(1)} year)`;
    return `${value} days`;
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        📊 Quick Historical Analysis
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Quick Analysis Module</strong><br />
        Fast, lightweight analysis using historical rainfall and river discharge data from ISIMIP. Perfect for:
        • Quick risk assessments • Local data analysis with 10 Malaysian locations • Seasonal pattern identification (monsoon cycles) • Historical flood event probability calculation
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Data Source</InputLabel>
            <Select
              value={dataSource}
              onChange={(e) => setDataSource(e.target.value)}
              label="Data Source"
            >
              <MenuItem value="ISIMIP Historical Data">ISIMIP Historical Data</MenuItem>
              <MenuItem value="Generate Sample Data">Generate Sample Data</MenuItem>
              <MenuItem value="Upload CSV File">Upload CSV File</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          {dataSource === 'ISIMIP Historical Data' && (
            <FormControl fullWidth>
              <InputLabel>Location</InputLabel>
              <Select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                label="Location"
              >
                {locations.quick_analysis?.map((loc) => (
                  <MenuItem key={loc} value={loc}>{loc}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          {dataSource === 'Generate Sample Data' && (
            <FormControl fullWidth>
              <InputLabel>Region</InputLabel>
              <Select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                label="Region"
              >
                {locations.regions?.map((reg) => (
                  <MenuItem key={reg} value={reg}>{reg.charAt(0).toUpperCase() + reg.slice(1)}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          {dataSource === 'Upload CSV File' && (
            <TextField
              type="file"
              fullWidth
              inputProps={{ accept: '.csv' }}
              onChange={handleFileUpload}
              helperText="Upload CSV with 'date' and 'rainfall' columns"
            />
          )}
        </Grid>

        {dataSource !== 'Upload CSV File' && (
          <Grid item xs={12}>
            <Typography gutterBottom>Years of Data: {years}</Typography>
            <Slider
              value={years}
              onChange={(e, value) => setYears(value)}
              min={dataSource === 'ISIMIP Historical Data' ? 10 : 5}
              max={dataSource === 'ISIMIP Historical Data' ? 50 : 20}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <Button
            variant="contained"
            onClick={handleDataGeneration}
            disabled={loading || (dataSource === 'Upload CSV File' && !uploadedFile)}
            startIcon={loading ? <CircularProgress size={20} /> : null}
            size="large"
          >
            {loading ? 'Loading...' : '🚀 Load Data'}
          </Button>
        </Grid>
      </Grid>

      {data && (
        <Box sx={{ mt: 4 }}>
          <Alert severity="success" sx={{ mb: 3 }}>
            {data.message}
          </Alert>

          {data.data_summary && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{data.data_summary.total_days?.toLocaleString() || 'N/A'}</Typography>
                    <Typography color="text.secondary">Total Days</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{data.data_summary.date_range || 'N/A'}</Typography>
                    <Typography color="text.secondary">Date Range</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{data.data_summary.avg_rainfall?.toFixed(1) || 'N/A'} mm</Typography>
                    <Typography color="text.secondary">Avg Rainfall</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{data.data_summary.max_rainfall?.toFixed(1) || 'N/A'} mm</Typography>
                    <Typography color="text.secondary">Max Rainfall</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {rainfallTimeseries && (
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>🌧️ Rainfall Time Series</Typography>
              <Plot
                data={[
                  {
                    x: rainfallTimeseries.dates,
                    y: rainfallTimeseries.rainfall,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Daily Rainfall',
                    line: { color: '#1f77b4', width: 1 }
                  }
                ]}
                layout={{
                  title: 'Daily Rainfall Over Time',
                  xaxis: { title: 'Date' },
                  yaxis: { title: 'Rainfall (mm)' },
                  height: 400,
                  hovermode: 'x unified',
                  shapes: [
                    {
                      type: 'line',
                      x0: rainfallTimeseries.dates[0],
                      x1: rainfallTimeseries.dates[rainfallTimeseries.dates.length - 1],
                      y0: 100,
                      y1: 100,
                      line: { color: 'orange', width: 2, dash: 'dash' }
                    },
                    {
                      type: 'line',
                      x0: rainfallTimeseries.dates[0],
                      x1: rainfallTimeseries.dates[rainfallTimeseries.dates.length - 1],
                      y0: 150,
                      y1: 150,
                      line: { color: 'red', width: 2, dash: 'dash' }
                    }
                  ],
                  annotations: [
                    {
                      x: rainfallTimeseries.dates[Math.floor(rainfallTimeseries.dates.length * 0.8)],
                      y: 100,
                      text: 'Heavy Rainfall (100mm)',
                      showarrow: false,
                      yshift: 10
                    },
                    {
                      x: rainfallTimeseries.dates[Math.floor(rainfallTimeseries.dates.length * 0.8)],
                      y: 150,
                      text: 'Flood Threshold (150mm)',
                      showarrow: false,
                      yshift: 10
                    }
                  ]
                }}
                style={{ width: '100%' }}
                config={{ responsive: true }}
              />
            </Paper>
          )}

          {dischargeTimeseries && (
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>🌊 River Discharge Time Series</Typography>
              <Plot
                data={[
                  {
                    x: dischargeTimeseries.dates,
                    y: dischargeTimeseries.discharge,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'River Discharge',
                    line: { color: '#2ca02c', width: 1 }
                  }
                ]}
                layout={{
                  title: 'Daily River Discharge Over Time',
                  xaxis: { title: 'Date' },
                  yaxis: { title: 'Discharge (m³/s)' },
                  height: 400,
                  hovermode: 'x unified'
                }}
                style={{ width: '100%' }}
                config={{ responsive: true }}
              />
              
              {dischargeTimeseries.stats && (
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Avg Discharge:</strong> {dischargeTimeseries.stats.avg_discharge.toFixed(1)} m³/s
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Max Discharge:</strong> {dischargeTimeseries.stats.max_discharge.toFixed(1)} m³/s
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Min Discharge:</strong> {dischargeTimeseries.stats.min_discharge.toFixed(1)} m³/s
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </Paper>
          )}

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🔍 Probability Analysis</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography gutterBottom>Time Window: {formatTimeWindow(timeWindow)}</Typography>
                  <Slider
                    value={timeWindow}
                    onChange={(e, value) => setTimeWindow(value)}
                    min={7}
                    max={365}
                    marks={[
                      { value: 7, label: '7d' },
                      { value: 30, label: '30d' },
                      { value: 90, label: '90d' },
                      { value: 180, label: '180d' },
                      { value: 365, label: '365d' }
                    ]}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatTimeWindow}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Event Types</InputLabel>
                    <Select
                      multiple
                      value={eventTypes}
                      onChange={handleEventTypeChange}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip key={value} label={value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} />
                          ))}
                        </Box>
                      )}
                    >
                      <MenuItem value="flood">Flood</MenuItem>
                      <MenuItem value="heavy_rainfall">Heavy Rainfall</MenuItem>
                      <MenuItem value="extreme_rainfall">Extreme Rainfall</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    onClick={handleProbabilityAnalysis}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : null}
                  >
                    {loading ? 'Analyzing...' : '🚀 Calculate Probabilities'}
                  </Button>
                </Grid>
              </Grid>

              {probabilities && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>📊 Probability Results</Typography>
                  <Grid container spacing={2}>
                    {Object.entries(probabilities).map(([event, prob]) => (
                      <Grid item xs={12} sm={4} key={event}>
                        <Card>
                          <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary">
                              {(prob * 100).toFixed(1)}%
                            </Typography>
                            <Typography color="text.secondary">
                              {event.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  <Paper sx={{ p: 2, mt: 3 }}>
                    <Plot
                      data={[
                        {
                          x: Object.keys(probabilities).map(e => e.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())),
                          y: Object.values(probabilities),
                          type: 'bar',
                          text: Object.values(probabilities).map(v => `${(v * 100).toFixed(1)}%`),
                          textposition: 'outside',
                          marker: {
                            color: ['#ff6b6b', '#4ecdc4', '#45b7d1'],
                            line: { color: 'white', width: 2 }
                          }
                        }
                      ]}
                      layout={{
                        title: `Event Probabilities (${timeWindow}-Day Window)`,
                        yaxis: { title: 'Probability', tickformat: '.0%' },
                        height: 400
                      }}
                      style={{ width: '100%' }}
                      config={{ responsive: true }}
                    />
                  </Paper>
                </Box>
              )}

              {seasonalData && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>🌏 Seasonal Analysis</Typography>
                  <Paper sx={{ p: 2 }}>
                    <Plot
                      data={[
                        {
                          x: seasonalData.map(s => s.season),
                          y: seasonalData.map(s => s.flood_probability),
                          type: 'bar',
                          text: seasonalData.map(s => `${(s.flood_probability * 100).toFixed(2)}%`),
                          textposition: 'outside',
                          marker: {
                            color: ['#e74c3c', '#f39c12', '#3498db']
                          }
                        }
                      ]}
                      layout={{
                        title: 'Seasonal Flood Risk',
                        yaxis: { title: 'Daily Flood Probability', tickformat: '.1%' },
                        height: 400
                      }}
                      style={{ width: '100%' }}
                      config={{ responsive: true }}
                    />
                  </Paper>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">📈 Trend Prediction</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    onClick={() => handleTrendPrediction('flood', 5)}
                    disabled={loading}
                  >
                    🔮 Predict 5-Year Flood Trend
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant="outlined"
                    onClick={() => handleTrendPrediction('heavy_rainfall', 10)}
                    disabled={loading}
                  >
                    🔮 Predict 10-Year Rainfall Trend
                  </Button>
                </Grid>
              </Grid>

              {trendPrediction && (
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6">{(trendPrediction.current_probability * 100).toFixed(1)}%</Typography>
                          <Typography color="text.secondary">Current Risk</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6">{(trendPrediction.predicted_probability * 100).toFixed(1)}%</Typography>
                          <Typography color="text.secondary">Predicted Risk</Typography>
                          <Typography variant="body2" color={
                            (trendPrediction.predicted_probability - trendPrediction.current_probability) > 0 ? 'error' : 'success'
                          }>
                            {((trendPrediction.predicted_probability - trendPrediction.current_probability) * 100).toFixed(1)}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6">{trendPrediction.trend?.toUpperCase()}</Typography>
                          <Typography color="text.secondary">Trend</Typography>
                          <Typography variant="body2">
                            Confidence: {trendPrediction.confidence?.toUpperCase()} (R² = {trendPrediction.r_squared?.toFixed(3)})
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        </Box>
      )}
    </Box>
  );
};

export default QuickAnalysis;