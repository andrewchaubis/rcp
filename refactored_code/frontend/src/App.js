import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Box, Tabs, Tab } from '@mui/material';
import QuickAnalysis from './components/QuickAnalysis';
import ClimadaAnalysis from './components/ClimadaAnalysis';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1f77b4',
    },
    secondary: {
      main: '#ff6b6b',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%)' }}>
          <Toolbar>
            <Typography variant="h4" component="div" sx={{ flexGrow: 1, color: '#1f77b4', textAlign: 'center' }}>
              🌧️ Malaysia Climate Risk Assessment Platform
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 2 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="analysis tabs">
              <Tab label="📊 Quick Analysis (Lightweight)" />
              <Tab label="🌍 CLIMADA Analysis (Advanced)" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <QuickAnalysis />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <ClimadaAnalysis />
          </TabPanel>
        </Container>

        <Box sx={{ mt: 4, py: 3, bgcolor: 'background.paper', textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Malaysia Climate Risk Assessment Platform</strong><br />
            Powered by CLIMADA Framework (ETH Zurich) | Data: Historical & Projected<br />
            Version 2.0 | Last Updated: 2025
          </Typography>
        </Box>
      </div>
    </ThemeProvider>
  );
}

export default App;