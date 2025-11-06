"""
FastAPI Backend for Malaysia Climate Risk Assessment Platform
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import json
import io
from datetime import datetime

# Import our climate analysis modules
from climate_probability import ClimateEventAnalyzer, generate_sample_data
from climate_probability_climada import ClimadaFloodAnalyzer, generate_climada_report
from isimip_probability import ISIMIPDataProcessor

app = FastAPI(
    title="Malaysia Climate Risk Assessment API",
    description="API for climate risk analysis and flood probability assessment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    data_source: str
    location: Optional[str] = None
    region: Optional[str] = None
    years: int = 10
    time_window: int = 365
    event_types: List[str] = ["flood", "heavy_rainfall", "extreme_rainfall"]

class ProbabilityResponse(BaseModel):
    probabilities: Dict[str, float]
    seasonal_analysis: Dict[str, Any]
    data_summary: Dict[str, Any]

class TrendRequest(BaseModel):
    event_type: str
    years_ahead: int = 5

class ClimadaRequest(BaseModel):
    location: str
    scenario: str = "historical"
    return_period: int = 100

class DataUploadResponse(BaseModel):
    message: str
    rows: int
    columns: List[str]

# Global storage for session data (in production, use proper session management)
session_data = {}

@app.get("/")
async def root():
    return {"message": "Malaysia Climate Risk Assessment API", "version": "1.0.0"}

@app.get("/api/locations")
async def get_locations():
    """Get available locations for analysis"""
    return {
        "quick_analysis": [
            "Malaysia (Country)", "Selangor", "Johor", "Kelantan", "Terengganu", 
            "Pahang", "Perak", "Penang", "Sabah", "Sarawak"
        ],
        "regions": ["peninsular", "sabah", "sarawak"],
        "climada_locations": [
            "Malaysia (Country)", "Selangor", "Johor", "Kelantan", "Terengganu", 
            "Pahang", "Perak", "Penang", "Sabah", "Sarawak"
        ]
    }

@app.get("/api/scenarios")
async def get_scenarios():
    """Get available climate scenarios"""
    return {
        "scenarios": [
            {"id": "historical", "name": "Historical Baseline", "description": "Historical climate conditions based on past observations"},
            {"id": "rcp26", "name": "RCP 2.6 (Strong Mitigation)", "description": "Best case scenario with aggressive climate action"},
            {"id": "rcp45", "name": "RCP 4.5 (Moderate)", "description": "Moderate emissions scenario - most likely pathway"},
            {"id": "rcp60", "name": "RCP 6.0 (Medium-High)", "description": "Limited emissions reductions"},
            {"id": "rcp85", "name": "RCP 8.5 (High Emissions)", "description": "Business as usual, minimal climate action"}
        ]
    }

@app.post("/api/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload CSV data for analysis"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        if 'date' not in df.columns or 'rainfall' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'date' and 'rainfall' columns")
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Store in session (in production, use proper storage)
        session_id = f"upload_{datetime.now().timestamp()}"
        session_data[session_id] = df
        
        return DataUploadResponse(
            message=f"Data uploaded successfully. Session ID: {session_id}",
            rows=len(df),
            columns=df.columns.tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/api/generate-data")
async def generate_data(request: AnalysisRequest):
    """Generate sample or ISIMIP data for analysis"""
    try:
        if request.data_source == "ISIMIP Historical Data":
            processor = ISIMIPDataProcessor(location=request.location)
            rainfall_df, discharge_df = processor.generate_historical_data(years=request.years)
            
            # Convert to format expected by ClimateEventAnalyzer
            data = rainfall_df.copy()
            data = data.rename(columns={'rainfall_mm': 'rainfall'})
            
            # Store both datasets
            session_id = f"isimip_{datetime.now().timestamp()}"
            session_data[session_id] = {
                'rainfall': data,
                'discharge': discharge_df
            }
            
            return {
                "session_id": session_id,
                "message": f"Loaded ISIMIP Historical Data for {request.location}",
                "rainfall_records": len(data),
                "discharge_records": len(discharge_df),
                "years": request.years,
                "data_summary": {
                    "total_days": len(data),
                    "date_range": f"{data['date'].min().year} - {data['date'].max().year}",
                    "avg_rainfall": float(data['rainfall'].mean()),
                    "max_rainfall": float(data['rainfall'].max())
                }
            }
            
        elif request.data_source == "Generate Sample Data":
            data = generate_sample_data(years=request.years, location=request.region)
            
            session_id = f"sample_{datetime.now().timestamp()}"
            session_data[session_id] = {'rainfall': data}
            
            return {
                "session_id": session_id,
                "message": f"Generated {len(data)} days of sample rainfall data for {request.region.title()}",
                "data_summary": {
                    "total_days": len(data),
                    "date_range": f"{data['date'].min().year} - {data['date'].max().year}",
                    "avg_rainfall": float(data['rainfall'].mean()),
                    "max_rainfall": float(data['rainfall'].max())
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid data source")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")

@app.post("/api/analyze-probabilities")
async def analyze_probabilities(session_id: str, request: AnalysisRequest):
    """Calculate climate event probabilities"""
    try:
        if session_id not in session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data_dict = session_data[session_id]
        rainfall_data = data_dict.get('rainfall') if isinstance(data_dict, dict) else data_dict
        
        if rainfall_data is None:
            raise HTTPException(status_code=400, detail="No rainfall data found in session")
        
        # Create analyzer
        analyzer = ClimateEventAnalyzer(rainfall_data)
        
        # Calculate probabilities
        probabilities = analyzer.calculate_all_probabilities(request.time_window)
        
        # Filter selected event types
        filtered_probs = {k: v for k, v in probabilities.items() if k in request.event_types}
        
        # Seasonal analysis
        seasons = {
            'northeast_monsoon': 'Northeast Monsoon (Nov-Mar)',
            'southwest_monsoon': 'Southwest Monsoon (May-Sep)',
            'inter_monsoon': 'Inter-Monsoon (Apr, Oct)'
        }
        
        seasonal_data = []
        for season_key, season_name in seasons.items():
            prob = analyzer.get_seasonal_probability('flood', season_key)
            seasonal_data.append({
                'season': season_name,
                'flood_probability': prob,
                'risk_level': 'High' if prob > 0.1 else 'Medium' if prob > 0.05 else 'Low'
            })
        
        return {
            "probabilities": filtered_probs,
            "seasonal_analysis": seasonal_data,
            "time_window": request.time_window,
            "data_summary": {
                "total_days": len(rainfall_data),
                "avg_rainfall": float(rainfall_data['rainfall'].mean()),
                "max_rainfall": float(rainfall_data['rainfall'].max())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing probabilities: {str(e)}")

@app.post("/api/predict-trend")
async def predict_trend(session_id: str, request: TrendRequest):
    """Predict climate event trends"""
    try:
        if session_id not in session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data_dict = session_data[session_id]
        rainfall_data = data_dict.get('rainfall') if isinstance(data_dict, dict) else data_dict
        
        if rainfall_data is None:
            raise HTTPException(status_code=400, detail="No rainfall data found in session")
        
        analyzer = ClimateEventAnalyzer(rainfall_data)
        trend = analyzer.predict_trend(request.event_type, years_ahead=request.years_ahead)
        
        return trend
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting trend: {str(e)}")

@app.get("/api/rainfall-timeseries/{session_id}")
async def get_rainfall_timeseries(session_id: str):
    """Get rainfall time series data for plotting"""
    try:
        if session_id not in session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data_dict = session_data[session_id]
        rainfall_data = data_dict.get('rainfall') if isinstance(data_dict, dict) else data_dict
        
        if rainfall_data is None:
            raise HTTPException(status_code=400, detail="No rainfall data found in session")
        
        # Convert to JSON-serializable format
        timeseries = {
            'dates': rainfall_data['date'].dt.strftime('%Y-%m-%d').tolist(),
            'rainfall': rainfall_data['rainfall'].tolist()
        }
        
        return timeseries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting timeseries: {str(e)}")

@app.get("/api/discharge-timeseries/{session_id}")
async def get_discharge_timeseries(session_id: str):
    """Get river discharge time series data for plotting"""
    try:
        if session_id not in session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data_dict = session_data[session_id]
        if not isinstance(data_dict, dict) or 'discharge' not in data_dict:
            return {"message": "No discharge data available"}
        
        discharge_data = data_dict['discharge']
        
        # Convert to JSON-serializable format
        timeseries = {
            'dates': discharge_data['date'].dt.strftime('%Y-%m-%d').tolist(),
            'discharge': discharge_data['discharge_m3s'].tolist(),
            'stats': {
                'avg_discharge': float(discharge_data['discharge_m3s'].mean()),
                'max_discharge': float(discharge_data['discharge_m3s'].max()),
                'min_discharge': float(discharge_data['discharge_m3s'].min())
            }
        }
        
        return timeseries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting discharge timeseries: {str(e)}")

# CLIMADA Analysis endpoints
@app.post("/api/climada/analyze")
async def climada_analyze(request: ClimadaRequest):
    """Perform CLIMADA flood analysis"""
    try:
        analyzer = ClimadaFloodAnalyzer()
        
        # Get hazard data
        hazard_data = analyzer.get_flood_hazard(request.location, request.scenario)
        
        # Calculate expected annual impact
        eai_results = analyzer.calculate_expected_annual_impact(request.location)
        
        return {
            "location": request.location,
            "scenario": request.scenario,
            "hazard_data": hazard_data,
            "eai_results": eai_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in CLIMADA analysis: {str(e)}")

@app.post("/api/climada/compare-scenarios")
async def climada_compare_scenarios(location: str, return_period: int = 100):
    """Compare flood intensity across climate scenarios"""
    try:
        analyzer = ClimadaFloodAnalyzer()
        comparison = analyzer.compare_scenarios(location, return_period)
        
        return {
            "location": location,
            "return_period": return_period,
            "comparison": comparison.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(e)}")

@app.post("/api/climada/generate-report")
async def climada_generate_report(request: ClimadaRequest):
    """Generate comprehensive CLIMADA report"""
    try:
        report = generate_climada_report(request.location, request.scenario)
        
        return {
            "location": request.location,
            "scenario": request.scenario,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session data"""
    if session_id in session_data:
        del session_data[session_id]
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)