import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, FormControl, InputLabel, Select, MenuItem,
  Button, Alert, CircularProgress, Paper, Accordion, AccordionSummary, AccordionDetails,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Plot from 'react-plotly.js';
import { apiService } from '../services/api';

const ClimadaAnalysis = () => {
  const [locations, setLocations] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [location, setLocation] = useState('Malaysia (Country)');
  const [scenario, setScenario] = useState('historical');
  const [returnPeriod, setReturnPeriod] = useState(100);
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [scenarioComparison, setScenarioComparison] = useState(null);
  const [report, setReport] = useState(null);
  const [reportDialog, setReportDialog] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [locationsResponse, scenariosResponse] = await Promise.all([
        apiService.getLocations(),
        apiService.getScenarios()
      ]);
      setLocations(locationsResponse.data.climada_locations || []);
      setScenarios(scenariosResponse.data.scenarios || []);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const handleAnalysis = async () => {
    setLoading(true);
    try {
      const response = await apiService.climadaAnalyze({
        location,
        scenario,
        return_period: returnPeriod
      });
      setAnalysisResults(response.data);
    } catch (error) {
      console.error('Error performing CLIMADA analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioComparison = async () => {
    setLoading(true);
    try {
      const response = await apiService.climadaCompareScenarios(location, returnPeriod);
      setScenarioComparison(response.data);
    } catch (error) {
      console.error('Error comparing scenarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await apiService.climadaGenerateReport({
        location,
        scenario
      });
      setReport(response.data);
      setReportDialog(true);
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    if (!report) return;
    
    const element = document.createElement('a');
    const file = new Blob([report.report], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `climada_report_${location.toLowerCase().replace(' ', '_')}_${scenario}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getScenarioInfo = (scenarioId) => {
    return scenarios.find(s => s.id === scenarioId) || {};
  };

  const scenarioInfo = getScenarioInfo(scenario);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        🌍 CLIMADA-Enhanced Risk Assessment
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>CLIMADA Framework Integration</strong><br />
        Professional-grade risk assessment using ETH Zurich's CLIMADA framework:
        • Return period analysis (10-1000 years) • Climate scenario projections (RCP 2.6-8.5) • Expected Annual Impact calculations • Global hazard datasets
      </Alert>

      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">ℹ️ About Climate Scenarios & Methodology</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            <strong>Representative Concentration Pathways (RCPs)</strong><br />
            RCPs are greenhouse gas concentration trajectories used by the IPCC to model future climate change.
            Each represents a different level of climate change mitigation effort.
          </Typography>
          
          <Grid container spacing={2}>
            {scenarios.map((s) => (
              <Grid item xs={12} sm={6} md={3} key={s.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" color="primary">{s.name}</Typography>
                    <Typography variant="body2">{s.description}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Typography variant="body2" sx={{ mt: 2 }}>
            <strong>How This Analysis Works:</strong><br />
            1. <strong>Flood Hazard Data:</strong> Global datasets from climate models showing expected flood depths<br />
            2. <strong>Exposure Data:</strong> Economic value of assets in each Malaysian state (buildings, infrastructure)<br />
            3. <strong>Return Periods:</strong> Statistical analysis of how frequently floods of different magnitudes occur<br />
            4. <strong>Expected Annual Impact (EAI):</strong> Average financial losses per year from flooding<br />
            5. <strong>Climate Scenarios:</strong> Projections showing how flood risk changes under different climate futures
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Location</InputLabel>
            <Select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              label="Location"
            >
              {locations.map((loc) => (
                <MenuItem key={loc} value={loc}>{loc}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Climate Scenario</InputLabel>
            <Select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              label="Climate Scenario"
            >
              {scenarios.map((s) => (
                <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Return Period (years)</InputLabel>
            <Select
              value={returnPeriod}
              onChange={(e) => setReturnPeriod(e.target.value)}
              label="Return Period (years)"
            >
              <MenuItem value={10}>10 years</MenuItem>
              <MenuItem value={25}>25 years</MenuItem>
              <MenuItem value={50}>50 years</MenuItem>
              <MenuItem value={100}>100 years</MenuItem>
              <MenuItem value={250}>250 years</MenuItem>
              <MenuItem value={500}>500 years</MenuItem>
              <MenuItem value={1000}>1000 years</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {scenarioInfo && (
        <Card sx={{ mt: 2, bgcolor: 'background.paper' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {scenarioInfo.name}
            </Typography>
            <Typography variant="body2">
              {scenarioInfo.description}
            </Typography>
          </CardContent>
        </Card>
      )}

      <Box sx={{ mt: 3 }}>
        <Grid container spacing={2}>
          <Grid item>
            <Button
              variant="contained"
              onClick={handleAnalysis}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Analyzing...' : '🚀 Run CLIMADA Analysis'}
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              onClick={handleScenarioComparison}
              disabled={loading}
            >
              🌡️ Compare All Scenarios
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              onClick={handleGenerateReport}
              disabled={loading}
            >
              📋 Generate Full Report
            </Button>
          </Grid>
        </Grid>
      </Box>

      {analysisResults && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>📊 Analysis Results</Typography>
          
          {analysisResults.hazard_data && (
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>🌊 Flood Hazard Analysis</Typography>
              <Plot
                data={[
                  {
                    x: analysisResults.hazard_data.return_period || [],
                    y: analysisResults.hazard_data.flood_intensity_m || [],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Flood Depth',
                    line: { color: '#3498db', width: 3 },
                    marker: { size: 10 }
                  }
                ]}
                layout={{
                  title: `Flood Intensity vs Return Period - ${location}`,
                  xaxis: { title: 'Return Period (years)', type: 'log' },
                  yaxis: { title: 'Flood Depth (meters)' },
                  height: 400,
                  hovermode: 'x unified'
                }}
                style={{ width: '100%' }}
                config={{ responsive: true }}
              />
            </Paper>
          )}

          {analysisResults.eai_results && (
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>💰 Financial Risk Assessment</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        ${(analysisResults.eai_results.exposure_usd / 1e9).toFixed(2)}B
                      </Typography>
                      <Typography color="text.secondary">Exposure</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        ${(analysisResults.eai_results.expected_annual_impact_usd / 1e6).toFixed(1)}M
                      </Typography>
                      <Typography color="text.secondary">Expected Annual Impact</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        {(analysisResults.eai_results.eai_ratio * 100).toFixed(2)}%
                      </Typography>
                      <Typography color="text.secondary">EAI/Exposure Ratio</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>Interpretation:</strong> On average, approximately{' '}
                <strong>{(analysisResults.eai_results.eai_ratio * 100).toFixed(2)}%</strong> of exposed assets in{' '}
                {location} could be damaged annually due to floods under the {scenario.toUpperCase()} scenario.
              </Alert>
            </Paper>
          )}
        </Box>
      )}

      {scenarioComparison && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>🌡️ Climate Scenario Comparison</Typography>
          <Paper sx={{ p: 2 }}>
            <Plot
              data={[
                {
                  x: scenarioComparison.comparison.map(c => c.scenario),
                  y: scenarioComparison.comparison.map(c => c.flood_intensity_m),
                  type: 'bar',
                  text: scenarioComparison.comparison.map(c => `${c.flood_intensity_m.toFixed(2)}m`),
                  textposition: 'outside',
                  marker: {
                    color: ['#95a5a6', '#27ae60', '#f39c12', '#e67e22', '#e74c3c']
                  }
                }
              ]}
              layout={{
                title: `${returnPeriod}-Year Flood Intensity by Climate Scenario`,
                xaxis: { title: 'Scenario' },
                yaxis: { title: 'Flood Depth (meters)' },
                height: 400
              }}
              style={{ width: '100%' }}
              config={{ responsive: true }}
            />
            
            <Box sx={{ mt: 2, overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '8px', border: '1px solid #ddd' }}>Scenario</th>
                    <th style={{ padding: '8px', border: '1px solid #ddd' }}>Flood Intensity (m)</th>
                    <th style={{ padding: '8px', border: '1px solid #ddd' }}>Annual Probability</th>
                    <th style={{ padding: '8px', border: '1px solid #ddd' }}>Intensity Change (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {scenarioComparison.comparison.map((row, index) => (
                    <tr key={index}>
                      <td style={{ padding: '8px', border: '1px solid #ddd' }}>{row.scenario}</td>
                      <td style={{ padding: '8px', border: '1px solid #ddd' }}>{row.flood_intensity_m.toFixed(2)}m</td>
                      <td style={{ padding: '8px', border: '1px solid #ddd' }}>{(row.annual_probability * 100).toFixed(3)}%</td>
                      <td style={{ padding: '8px', border: '1px solid #ddd' }}>{row.intensity_change_pct > 0 ? '+' : ''}{row.intensity_change_pct.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Paper>
        </Box>
      )}

      <Dialog open={reportDialog} onClose={() => setReportDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>📄 CLIMADA Risk Assessment Report</DialogTitle>
        <DialogContent>
          {report && (
            <TextField
              multiline
              rows={20}
              fullWidth
              value={report.report}
              variant="outlined"
              InputProps={{
                readOnly: true,
                style: { fontFamily: 'monospace', fontSize: '0.875rem' }
              }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialog(false)}>Close</Button>
          <Button onClick={downloadReport} variant="contained">
            💾 Download Report
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ClimadaAnalysis;