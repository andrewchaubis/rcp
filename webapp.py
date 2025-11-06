"""
Climate Risk Assessment Web Application for Malaysia
Interactive dashboard for flood and rainfall probability analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys

# Import our modules
from climate_probability import ClimateEventAnalyzer, generate_sample_data
from climate_probability_climada import ClimadaFloodAnalyzer, generate_climada_report

# Page configuration
st.set_page_config(
    page_title="Malaysia Climate Risk Assessment",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🌧️ Malaysia Climate Risk Assessment Platform</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuration")

# Module selection
analysis_type = st.sidebar.radio(
    "Analysis Module",
    ["📊 Quick Analysis (Lightweight)", "🌍 CLIMADA Analysis (Advanced)"],
    help="Choose between quick historical analysis or advanced CLIMADA-based assessment"
)

st.sidebar.markdown("---")

# Main content
if "📊 Quick Analysis" in analysis_type:
    st.header("📊 Quick Historical Analysis")
    
    st.markdown("""
    <div class="info-box">
    <b>Quick Analysis Module</b><br>
    Fast, lightweight analysis using historical rainfall and river discharge data from ISIMIP. Perfect for:
    • Quick risk assessments
    • Local data analysis with 10 Malaysian locations
    • Seasonal pattern identification (monsoon cycles)
    • Historical flood event probability calculation
    </div>
    """, unsafe_allow_html=True)
    
    # Data source selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        data_source = st.selectbox(
            "Data Source",
            ["ISIMIP Historical Data", "Generate Sample Data", "Upload CSV File"],
            help="ISIMIP provides historical rainfall and river discharge data for Malaysia"
        )
    
    with col2:
        if data_source == "ISIMIP Historical Data":
            location_quick = st.selectbox(
                "Location",
                ["Malaysia (Country)", "Selangor", "Johor", "Kelantan", "Terengganu", 
                 "Pahang", "Perak", "Penang", "Sabah", "Sarawak"],
                key="quick_location"
            )
            years = st.slider("Years of Historical Data", 10, 50, 30, key="isimip_years")
        elif data_source == "Generate Sample Data":
            region = st.selectbox(
                "Region",
                ["peninsular", "sabah", "sarawak"],
                format_func=lambda x: x.title()
            )
            years = st.slider("Years of Data", 5, 20, 10)
    
    # Generate or load data
    if data_source == "ISIMIP Historical Data":
        with st.spinner("Loading ISIMIP historical data..."):
            # Import ISIMIP processor
            from isimip_probability import ISIMIPDataProcessor
            
            processor = ISIMIPDataProcessor(location=location_quick)
            rainfall_df, discharge_df = processor.generate_historical_data(years=years)
            
            # Convert to format expected by ClimateEventAnalyzer
            data = rainfall_df.copy()
            data = data.rename(columns={'rainfall_mm': 'rainfall'})
            
            st.success(f"""
✓ **Loaded ISIMIP Historical Data**
- Location: {location_quick}
- Rainfall records: {len(data):,} days
- River discharge records: {len(discharge_df):,} days
- Time period: {years} years
- Data source: ISIMIP-based historical climate analysis
            """)
            
            # Store discharge data in session state for later use
            st.session_state['discharge_data'] = discharge_df
            
    elif data_source == "Generate Sample Data":
        with st.spinner("Generating sample data..."):
            data = generate_sample_data(years=years, location=region)
            st.success(f"✓ Generated {len(data):,} days of sample rainfall data for {region.title()}")
    else:
        uploaded_file = st.file_uploader("Upload CSV with 'date' and 'rainfall' columns", type=['csv'])
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            data['date'] = pd.to_datetime(data['date'])
            st.success(f"✓ Loaded {len(data):,} days of data")
        else:
            st.info("Please upload a CSV file to continue")
            data = None
    
    if data is not None:
        # Create analyzer
        analyzer = ClimateEventAnalyzer(data)
        
        # Display data summary
        st.subheader("📈 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Days", f"{len(data):,}")
        with col2:
            st.metric("Date Range", f"{data['date'].min().year} - {data['date'].max().year}")
        with col3:
            st.metric("Avg Rainfall", f"{data['rainfall'].mean():.1f} mm")
        with col4:
            st.metric("Max Rainfall", f"{data['rainfall'].max():.1f} mm")
        
        # Rainfall time series
        st.subheader("🌧️ Rainfall Time Series")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['date'], 
            y=data['rainfall'],
            mode='lines',
            name='Daily Rainfall',
            line=dict(color='#1f77b4', width=1)
        ))
        
        # Add threshold lines
        fig.add_hline(y=100, line_dash="dash", line_color="orange", 
                      annotation_text="Heavy Rainfall (100mm)")
        fig.add_hline(y=150, line_dash="dash", line_color="red", 
                      annotation_text="Flood Threshold (150mm)")
        
        fig.update_layout(
            title="Daily Rainfall Over Time",
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show river discharge if ISIMIP data is loaded
        if data_source == "ISIMIP Historical Data" and 'discharge_data' in st.session_state:
            st.subheader("🌊 River Discharge Time Series")
            
            discharge_df = st.session_state['discharge_data']
            
            fig_discharge = go.Figure()
            fig_discharge.add_trace(go.Scatter(
                x=discharge_df['date'], 
                y=discharge_df['discharge_m3s'],
                mode='lines',
                name='River Discharge',
                line=dict(color='#2ca02c', width=1)
            ))
            
            fig_discharge.update_layout(
                title="Daily River Discharge Over Time",
                xaxis_title="Date",
                yaxis_title="Discharge (m³/s)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_discharge, use_container_width=True)
            
            # Add discharge statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Discharge", f"{discharge_df['discharge_m3s'].mean():.1f} m³/s")
            with col2:
                st.metric("Max Discharge", f"{discharge_df['discharge_m3s'].max():.1f} m³/s")
            with col3:
                st.metric("Min Discharge", f"{discharge_df['discharge_m3s'].min():.1f} m³/s")
        
        # Analysis options
        st.subheader("🔍 Probability Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            time_window = st.select_slider(
                "Time Window",
                options=[7, 14, 30, 90, 180, 365],
                value=365,
                format_func=lambda x: f"{x} days ({x/365:.1f} year)" if x >= 30 else f"{x} days"
            )
        
        with col2:
            event_types = st.multiselect(
                "Event Types",
                ["flood", "heavy_rainfall", "extreme_rainfall"],
                default=["flood", "heavy_rainfall", "extreme_rainfall"],
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        if st.button("🚀 Calculate Probabilities", type="primary"):
            with st.spinner("Analyzing..."):
                # Calculate probabilities
                probabilities = analyzer.calculate_all_probabilities(time_window)
                
                # Filter selected event types
                filtered_probs = {k: v for k, v in probabilities.items() if k in event_types}
                
                # Display results
                st.subheader("📊 Probability Results")
                
                cols = st.columns(len(filtered_probs))
                
                for idx, (event, prob) in enumerate(sorted(filtered_probs.items())):
                    with cols[idx]:
                        st.metric(
                            event.replace("_", " ").title(),
                            f"{prob*100:.1f}%",
                            delta=None
                        )
                
                # Probability chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=[e.replace("_", " ").title() for e in filtered_probs.keys()],
                        y=list(filtered_probs.values()),
                        text=[f"{v*100:.1f}%" for v in filtered_probs.values()],
                        textposition='outside',
                        marker=dict(
                            color=['#ff6b6b', '#4ecdc4', '#45b7d1'],
                            line=dict(color='white', width=2)
                        )
                    )
                ])
                
                fig.update_layout(
                    title=f"Event Probabilities ({time_window}-Day Window)",
                    yaxis_title="Probability",
                    yaxis_tickformat='.0%',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Seasonal analysis
        st.subheader("🌏 Seasonal Analysis")
        
        seasons = {
            'northeast_monsoon': 'Northeast Monsoon (Nov-Mar)',
            'southwest_monsoon': 'Southwest Monsoon (May-Sep)',
            'inter_monsoon': 'Inter-Monsoon (Apr, Oct)'
        }
        
        seasonal_data = []
        
        for season_key, season_name in seasons.items():
            prob = analyzer.get_seasonal_probability('flood', season_key)
            seasonal_data.append({
                'Season': season_name,
                'Flood Probability': prob,
                'Risk Level': 'High' if prob > 0.1 else 'Medium' if prob > 0.05 else 'Low'
            })
        
        seasonal_df = pd.DataFrame(seasonal_data)
        
        fig = go.Figure(data=[
            go.Bar(
                x=seasonal_df['Season'],
                y=seasonal_df['Flood Probability'],
                text=[f"{v*100:.2f}%" for v in seasonal_df['Flood Probability']],
                textposition='outside',
                marker=dict(
                    color=['#e74c3c', '#f39c12', '#3498db'],
                )
            )
        ])
        
        fig.update_layout(
            title="Seasonal Flood Risk",
            yaxis_title="Daily Flood Probability",
            yaxis_tickformat='.1%',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis
        st.subheader("📈 Trend Prediction")
        
        years_ahead = st.slider("Forecast Years Ahead", 1, 20, 5)
        
        if st.button("🔮 Predict Trends"):
            with st.spinner("Calculating trends..."):
                trend = analyzer.predict_trend('flood', years_ahead=years_ahead)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Risk", f"{trend['current_probability']*100:.1f}%")
                with col2:
                    change = (trend['predicted_probability'] - trend['current_probability']) * 100
                    st.metric(
                        f"Predicted Risk ({years_ahead}y)",
                        f"{trend['predicted_probability']*100:.1f}%",
                        delta=f"{change:+.1f}%"
                    )
                with col3:
                    st.metric("Trend", trend['trend'].upper())
                
                st.info(f"**Confidence:** {trend['confidence'].upper()} (R² = {trend['r_squared']:.3f})")

else:  # CLIMADA Analysis
    st.header("🌍 CLIMADA-Enhanced Risk Assessment")
    
    st.markdown("""
    <div class="info-box">
    <b>CLIMADA Framework Integration</b><br>
    Professional-grade risk assessment using ETH Zurich's CLIMADA framework:
    • Return period analysis (10-1000 years)
    • Climate scenario projections (RCP 2.6-8.5)
    • Expected Annual Impact calculations
    • Global hazard datasets
    </div>
    """, unsafe_allow_html=True)
    
    # Add expandable info section
    with st.expander("ℹ️ About Climate Scenarios & Methodology", expanded=False):
        st.markdown("""
        ### 🌡️ Representative Concentration Pathways (RCPs)
        
        RCPs are greenhouse gas concentration trajectories used by the IPCC to model future climate change. 
        Each represents a different level of climate change mitigation effort.
        
        **RCP 2.6** 🌱 - Strong Mitigation
        - Aggressive emissions reductions starting immediately
        - Global cooperation on climate action (Paris Agreement success)
        - Peak emissions before 2020, then rapid decline
        - Temperature increase: +1.0°C by 2100
        - **Likelihood:** Requires unprecedented global action
        
        **RCP 4.5** 🌍 - Moderate Scenario (Most Likely)
        - Moderate emissions reductions implemented
        - Some climate policies enacted globally
        - Emissions peak around 2040, then decline
        - Temperature increase: +1.8°C by 2100
        - **Likelihood:** Current trajectory if policies improve
        
        **RCP 6.0** ⚠️ - Medium-High Emissions
        - Limited emissions reductions
        - Some climate policies but insufficient
        - Emissions peak around 2060, then stabilize
        - Temperature increase: +2.2°C by 2100
        - **Likelihood:** If current policies don't improve
        
        **RCP 8.5** 🔥 - High Emissions (Worst Case)
        - Business as usual, minimal climate action
        - Continued high fossil fuel use
        - Emissions continue rising through 2100
        - Temperature increase: +3.7°C by 2100
        - **Likelihood:** Increasingly unlikely but used for stress testing
        
        ---
        
        ### 📊 How This Analysis Works
        
        1. **Flood Hazard Data**: Global datasets from climate models showing expected flood depths
        2. **Exposure Data**: Economic value of assets in each Malaysian state (buildings, infrastructure)
        3. **Return Periods**: Statistical analysis of how frequently floods of different magnitudes occur
        4. **Expected Annual Impact (EAI)**: Average financial losses per year from flooding
        5. **Climate Scenarios**: Projections showing how flood risk changes under different climate futures
        
        ---
        
        ### 🇲🇾 Malaysian Context
        
        **High-Risk Regions:**
        - **East Coast** (Kelantan, Terengganu, Pahang): Northeast monsoon brings intense rainfall Nov-Mar
        - **Urban Areas** (Selangor): Flash flooding from development and drainage issues
        - **River Systems** (Pahang): Large river basins susceptible to overflow
        
        **Climate Impacts:**
        - More intense monsoon rainfall expected under all RCP scenarios
        - Sea level rise affecting coastal areas (not included in flood depth analysis)
        - Increased frequency of extreme rainfall events
        
        ---
        
        ### 📖 Data Sources
        
        - **CLIMADA Framework**: ETH Zurich (climada.ethz.ch)
        - **Flood Hazard**: ISIMIP global flood models
        - **Exposure**: LitPop methodology (GDP & population-based)
        - **Climate Scenarios**: IPCC AR5 RCP projections
        """)
    
    # Location selection - Malaysian states
    location = st.selectbox(
        "Location",
        ["Malaysia (Country)", "Selangor", "Johor", "Kelantan", "Terengganu", 
         "Pahang", "Perak", "Penang", "Sabah", "Sarawak"]
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        scenario = st.selectbox(
            "Climate Scenario",
            ["historical", "rcp26", "rcp45", "rcp60", "rcp85"],
            format_func=lambda x: {
                'historical': 'Historical Baseline',
                'rcp26': 'RCP 2.6 (Strong Mitigation)',
                'rcp45': 'RCP 4.5 (Moderate)',
                'rcp60': 'RCP 6.0 (Medium-High)',
                'rcp85': 'RCP 8.5 (High Emissions)'
            }[x]
        )
        
        # Display detailed information about selected scenario
        scenario_info = {
            'historical': {
                'icon': '📊',
                'description': 'Historical climate conditions based on past observations',
                'timeframe': 'Based on 1980-2010 baseline period',
                'emissions': 'Not applicable',
                'temp_change': 'Baseline reference (0°C)',
                'use_case': 'Understanding current flood risk and validating models'
            },
            'rcp26': {
                'icon': '🌱',
                'description': 'Best case scenario with aggressive climate action',
                'timeframe': 'Projections for 2081-2100',
                'emissions': 'Peak at ~490 ppm CO₂ then decline',
                'temp_change': '+1.0°C by 2100 (Paris Agreement target)',
                'use_case': 'Planning for successful global climate mitigation'
            },
            'rcp45': {
                'icon': '🌍',
                'description': 'Moderate emissions scenario - most likely pathway',
                'timeframe': 'Projections for 2081-2100',
                'emissions': 'Stabilize at ~650 ppm CO₂',
                'temp_change': '+1.8°C by 2100',
                'use_case': 'Realistic planning baseline for infrastructure'
            },
            'rcp60': {
                'icon': '⚠️',
                'description': 'Medium-high emissions without strong mitigation',
                'timeframe': 'Projections for 2081-2100',
                'emissions': 'Stabilize at ~850 ppm CO₂',
                'temp_change': '+2.2°C by 2100',
                'use_case': 'Risk assessment for delayed climate action'
            },
            'rcp85': {
                'icon': '🔥',
                'description': 'Worst case scenario - business as usual',
                'timeframe': 'Projections for 2081-2100',
                'emissions': 'Rise to >1370 ppm CO₂',
                'temp_change': '+3.7°C by 2100',
                'use_case': 'Stress testing and worst-case flood defense planning'
            }
        }
        
        info = scenario_info[scenario]
        st.info(f"""
**{info['icon']} {info['description']}**

**Timeframe:** {info['timeframe']}  
**Emissions:** {info['emissions']}  
**Temperature Change:** {info['temp_change']}  
**Best Used For:** {info['use_case']}
        """)
    
    with col2:
        # ISIMIP-based automatic calculation
        use_auto_calculation = st.checkbox(
            "🤖 Auto-calculate return periods from ISIMIP data",
            value=True,
            help="Uses historical rainfall and river discharge data to automatically calculate return periods"
        )
        
        if not use_auto_calculation:
            return_periods = st.multiselect(
                "Return Periods (years) - Manual",
                [10, 25, 50, 100, 250],
                default=[10, 50, 100]
            )
        else:
            return_periods = None  # Will be auto-calculated
            st.success("✓ Return periods will be automatically calculated based on historical data")
        
        # Explain return periods and ISIMIP method
        st.info("""
**📅 Understanding Return Periods**

A return period indicates how often a flood of a certain magnitude is expected to occur on average.

**ISIMIP-Based Calculation:**
When auto-calculation is enabled, return periods are determined using:
- 🌧️ **Historical rainfall data** (50 years)
- 🌊 **River discharge observations**
- 📊 **Extreme Value Analysis** (GEV distribution)
- 📍 **Location-specific risk assessment**

**Examples:**
- **10-year flood:** 10% chance per year (frequent)
- **50-year flood:** 2% chance per year (moderate)
- **100-year flood:** 1% chance per year (rare)
- **250-year flood:** 0.4% chance per year (very rare)

⚠️ **Important:** A "100-year flood" doesn't mean it only happens once per century - it could occur multiple times in that period or not at all. It's a probability measure.

**For Planning:**
- **10-25 years:** Annual planning, maintenance
- **50 years:** Infrastructure design standard
- **100 years:** Critical infrastructure (hospitals)
- **250 years:** Stress testing, worst-case scenarios
        """)
    
    if st.button("🚀 Run CLIMADA Analysis", type="primary"):
        with st.spinner("Loading CLIMADA data and performing analysis..."):
            # Validate inputs
            if not use_auto_calculation and (return_periods is None or len(return_periods) == 0):
                st.error("⚠️ Please select at least one return period or enable auto-calculation")
                st.stop()
            
            # Create analyzer with ISIMIP integration
            analyzer = ClimadaFloodAnalyzer(use_isimip=use_auto_calculation)
            
            # Load data
            hazard_data = analyzer.load_flood_hazard(
                scenario=scenario,
                return_periods=return_periods,
                location=location
            )
            exposure = analyzer.load_exposure()
            
            st.success("✓ CLIMADA data loaded successfully")
            
            # Display hazard data for location
            st.subheader("🌊 Flood Hazard Analysis")
            
            # Add explanation of flood intensity
            st.info("""
**Understanding Flood Intensity (Depth in Meters)**

The flood intensity represents the **expected water depth** during a flood event:

**Interpretation Guide:**
- **0.0 - 0.5m**: Minor flooding - ankle to knee deep water
  - Nuisance flooding, typically manageable
  - May cause minor property damage
  
- **0.5 - 1.0m**: Moderate flooding - knee to waist deep water
  - Significant disruption to daily activities
  - Ground floor property damage likely
  - Difficult to walk through, vehicles may stall
  
- **1.0 - 2.0m**: Major flooding - waist to head deep water
  - Severe property damage, ground floors submerged
  - Dangerous conditions, evacuation recommended
  - Structural damage to buildings possible
  
- **>2.0m**: Catastrophic flooding - exceeds human height
  - Life-threatening conditions
  - Widespread structural damage
  - Major infrastructure disruption
  - Emergency evacuation required

💡 **Note:** These depths are averages for the region. Actual depths can vary by specific location due to local topography, drainage systems, and urban development.
            """)
            
            loc_hazard = hazard_data[hazard_data['location'] == location].sort_values('return_period')
            
            # Display ISIMIP data source info if using auto-calculation
            if use_auto_calculation and not loc_hazard.empty:
                if 'data_source' in loc_hazard.columns and 'ISIMIP' in str(loc_hazard['data_source'].iloc[0]):
                    st.success(f"""
✓ **ISIMIP-Based Analysis Complete**
- Data source: Historical rainfall and river discharge (50 years)
- Method: Extreme Value Analysis (GEV distribution)
- Auto-calculated return periods: {sorted(loc_hazard['return_period'].unique().tolist())}
                    """)
                    
                    # Show additional ISIMIP metrics if available
                    if 'rainfall_return_level_mm' in loc_hazard.columns:
                        with st.expander("📊 View ISIMIP Analysis Details"):
                            st.markdown("### Rainfall Return Levels")
                            rain_cols = st.columns(len(loc_hazard))
                            for idx, (_, row) in enumerate(loc_hazard.iterrows()):
                                with rain_cols[idx]:
                                    st.metric(
                                        f"{int(row['return_period'])}-yr",
                                        f"{row['rainfall_return_level_mm']:.1f}mm",
                                        help=f"Expected max daily rainfall for {int(row['return_period'])}-year event"
                                    )
                            
                            st.markdown("### River Discharge Return Levels")
                            discharge_cols = st.columns(len(loc_hazard))
                            for idx, (_, row) in enumerate(loc_hazard.iterrows()):
                                with discharge_cols[idx]:
                                    st.metric(
                                        f"{int(row['return_period'])}-yr",
                                        f"{row['discharge_return_level_m3s']:.1f}m³/s",
                                        help=f"Expected peak discharge for {int(row['return_period'])}-year event"
                                    )
            
            if not loc_hazard.empty:
                # Get actual return periods from data
                actual_return_periods = sorted(loc_hazard['return_period'].unique().tolist())
                
                # Metrics
                cols = st.columns(len(actual_return_periods))
                
                for idx, rp in enumerate(actual_return_periods):
                    rp_data = loc_hazard[loc_hazard['return_period'] == rp]
                    if not rp_data.empty:
                        with cols[idx]:
                            depth = rp_data['flood_intensity_m'].values[0]
                            annual_prob = rp_data['annual_probability'].values[0]
                            
                            # Determine severity level for context
                            if depth < 0.5:
                                severity = "Minor"
                                emoji = "💧"
                            elif depth < 1.0:
                                severity = "Moderate"
                                emoji = "🌊"
                            elif depth < 2.0:
                                severity = "Major"
                                emoji = "⚠️"
                            else:
                                severity = "Catastrophic"
                                emoji = "🚨"
                            
                            st.metric(
                                f"{rp}-Year Flood",
                                f"{depth:.2f}m",
                                delta=f"{annual_prob*100:.2f}% annual prob"
                            )
                            st.caption(f"{emoji} {severity} flooding")
                
                # Return period curve
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=loc_hazard['return_period'],
                    y=loc_hazard['flood_intensity_m'],
                    mode='lines+markers',
                    name='Flood Depth',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=10)
                ))
                
                fig.update_layout(
                    title=f"Flood Intensity vs Return Period - {location}",
                    xaxis_title="Return Period (years)",
                    yaxis_title="Flood Depth (meters)",
                    xaxis_type="log",
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Scenario comparison
            st.subheader("🌡️ Climate Scenario Comparison")
            
            if st.button("Compare All Scenarios"):
                with st.spinner("Comparing scenarios..."):
                    comparison = analyzer.compare_scenarios(location, return_period=100)
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=comparison['scenario'],
                        y=comparison['flood_intensity_m'],
                        text=[f"{v:.2f}m" for v in comparison['flood_intensity_m']],
                        textposition='outside',
                        marker=dict(
                            color=['#95a5a6', '#27ae60', '#f39c12', '#e67e22', '#e74c3c']
                        )
                    ))
                    
                    fig.update_layout(
                        title="100-Year Flood Intensity by Climate Scenario",
                        xaxis_title="Scenario",
                        yaxis_title="Flood Depth (meters)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Table
                    st.dataframe(
                        comparison.style.format({
                            'flood_intensity_m': '{:.2f}m',
                            'annual_probability': '{:.3%}',
                            'intensity_change_pct': '{:+.1f}%'
                        }),
                        use_container_width=True
                    )
            
            # Expected Annual Impact
            st.subheader("💰 Financial Risk Assessment")
            
            eai_results = analyzer.calculate_expected_annual_impact(location)
            
            if eai_results:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Exposure",
                        f"${eai_results['exposure_usd']/1e9:.2f}B"
                    )
                
                with col2:
                    st.metric(
                        "Expected Annual Impact",
                        f"${eai_results['expected_annual_impact_usd']/1e6:.1f}M"
                    )
                
                with col3:
                    st.metric(
                        "EAI/Exposure Ratio",
                        f"{eai_results['eai_ratio']*100:.2f}%"
                    )
                
                st.info(f"""
                **Interpretation:** On average, approximately **{eai_results['eai_ratio']*100:.2f}%** 
                of exposed assets in {location} could be damaged annually due to floods under 
                the {scenario.upper()} scenario.
                """)
            
            # Generate full report
            st.subheader("📄 Comprehensive Report")
            
            if st.button("📋 Generate Full Report"):
                with st.spinner("Generating comprehensive report..."):
                    report = generate_climada_report(location, scenario)
                    
                    st.text_area("CLIMADA Risk Assessment Report", report, height=500)
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Report",
                        data=report,
                        file_name=f"climada_report_{location.lower().replace(' ', '_')}_{scenario}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>
    <b>Malaysia Climate Risk Assessment Platform</b><br>
    Powered by CLIMADA Framework (ETH Zurich) | Data: Historical & Projected<br>
    Version 2.0 | Last Updated: 2025
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("""
**Modules:**
- Quick Analysis: Lightweight historical data analysis
- CLIMADA: Advanced risk assessment with climate projections

**Features:**
- Probability calculations
- Seasonal patterns
- Trend predictions
- Return period analysis
- Climate scenarios
- Financial risk metrics
""")

st.sidebar.markdown("### 📚 Resources")
st.sidebar.markdown("""
- [CLIMADA Documentation](https://climada.ethz.ch/)
- [GitHub Repository](https://github.com/edkp-2025/Team1)
- [Integration Guide](CLIMADA_INTEGRATION.md)
""")
