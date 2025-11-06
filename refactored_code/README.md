# 🚀 Refactored Climate Risk Assessment Platform

This directory contains the modernized version of the Malaysia Climate Risk Assessment Platform, transformed from a Streamlit application into a professional FastAPI backend + React frontend architecture.

## 📁 Project Structure

```
refactored_code/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── climate_probability.py
│   ├── climate_probability_climada.py
│   ├── isimip_probability.py
│   ├── flood_damage_library/
│   └── processed_jrc_data/
└── frontend/               # React Frontend
    ├── src/
    │   ├── App.js          # Main React application
    │   ├── components/     # React components
    │   │   ├── QuickAnalysis.js
    │   │   └── ClimadaAnalysis.js
    │   └── services/
    │       └── api.js      # API service layer
    ├── public/
    ├── build/              # Production build
    ├── package.json
    └── vite.config.js
```

## 🔧 Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm run build
npm run preview
```

## 🌐 API Endpoints

The FastAPI backend provides comprehensive climate analysis endpoints:

- **Data Management**: `/api/locations`, `/api/generate-data`
- **Analysis**: `/api/analyze-probabilities`, `/api/predict-trend`
- **Visualization**: `/api/rainfall-timeseries/{session_id}`, `/api/discharge-timeseries/{session_id}`
- **CLIMADA Integration**: `/api/climada/analyze`, `/api/climada/compare-scenarios`

## 🎯 Features

### Quick Analysis Module
- ⚡ Lightweight historical data analysis
- 📊 Interactive time series visualization
- 🌧️ Rainfall and river discharge analysis
- 📈 Probability calculations and trend predictions

### CLIMADA Analysis Module
- 🌍 Professional-grade risk assessment
- 🔬 ETH Zurich's CLIMADA framework integration
- 📊 Return period analysis (10-1000 years)
- 🌡️ Climate scenario projections (RCP 2.6-8.5)

## 🚀 Deployment

The application is production-ready with:
- ✅ Optimized React build (5.2MB JS bundle)
- ✅ FastAPI with CORS configuration
- ✅ Professional Material-UI interface
- ✅ Interactive Plotly visualizations
- ✅ Complete API integration layer

## 🔄 Migration Benefits

1. **Scalability**: Separate backend/frontend architecture
2. **Performance**: Optimized React build vs. Streamlit overhead
3. **Flexibility**: RESTful API enables multiple frontend integrations
4. **Professional UI**: Modern Material-UI components
5. **Maintainability**: Clear separation of concerns
6. **Extensibility**: Easy to add new analysis modules

## 📊 Data Sources

- **ISIMIP Historical Data**: 30 years of climate data (1995-2025)
- **Malaysian Locations**: 10 supported regions
- **CLIMADA Framework**: Global hazard datasets
- **JRC Flood Damage**: Economic impact calculations

---

*This refactored version provides a robust, scalable foundation for climate risk assessment with modern web technologies.*