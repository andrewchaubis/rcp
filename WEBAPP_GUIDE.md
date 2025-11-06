# Web Application Guide

## 🌐 Malaysia Climate Risk Assessment Platform

An interactive web application for analyzing flood and rainfall risks in Malaysia, powered by Streamlit and integrated with the CLIMADA framework.

---

## Features

### 📊 Quick Analysis Module
- **Interactive Data Visualization**: Time series plots with threshold indicators
- **Probability Calculations**: Customizable time windows (7 days to 1 year)
- **Seasonal Analysis**: Monsoon pattern identification
- **Trend Predictions**: Future risk forecasting (1-20 years)
- **Data Options**: 
  - Generate sample data for testing
  - Upload your own CSV files

### 🌍 CLIMADA Analysis Module
- **Return Period Analysis**: 10 to 250-year flood events
- **Climate Scenarios**: Historical baseline + RCP 2.6/4.5/6.0/8.5 projections
- **Multi-Location Support**: 6 major Malaysian cities
- **Financial Risk**: Expected Annual Impact (EAI) calculations
- **Scenario Comparison**: Interactive charts comparing climate futures
- **Comprehensive Reports**: Downloadable risk assessment reports

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web App

```bash
streamlit run webapp.py
```

The app will automatically open in your browser at `http://localhost:8501`

### 3. For Remote Access

```bash
streamlit run webapp.py \
    --server.port 12000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false
```

Access at: `http://your-server-ip:12000`

---

## User Guide

### Quick Analysis Workflow

1. **Select Analysis Module**
   - Choose "Quick Analysis (Lightweight)" from sidebar

2. **Configure Data Source**
   - **Option A**: Generate sample data
     - Select region: Peninsular, Sabah, or Sarawak
     - Choose years of data: 5-20 years
   - **Option B**: Upload CSV file
     - Required columns: `date`, `rainfall`
     - Date format: YYYY-MM-DD
     - Rainfall in millimeters

3. **View Data Overview**
   - Total days analyzed
   - Date range
   - Average and maximum rainfall
   - Interactive time series chart

4. **Calculate Probabilities**
   - Select time window (7-365 days)
   - Choose event types:
     - Flood (≥150mm)
     - Heavy Rainfall (≥100mm)
     - Extreme Rainfall (≥200mm)
   - Click "Calculate Probabilities"

5. **Analyze Seasonal Patterns**
   - View flood risk by monsoon season
   - Northeast Monsoon (Nov-Mar): Highest risk
   - Southwest Monsoon (May-Sep): Lowest risk
   - Inter-Monsoon (Apr, Oct): Moderate risk

6. **Predict Future Trends**
   - Select forecast period (1-20 years)
   - View trend direction: Increasing/Stable/Decreasing
   - Check confidence level and R² value

### CLIMADA Analysis Workflow

1. **Select CLIMADA Module**
   - Choose "CLIMADA Analysis (Advanced)" from sidebar

2. **Configure Analysis**
   - **Location**: Choose from 6 major cities
     - Kuala Lumpur
     - Penang
     - Johor Bahru
     - Kota Bharu
     - Kuching
     - Kota Kinabalu
   
   - **Climate Scenario**:
     - Historical: Current baseline
     - RCP 2.6: Strong mitigation (best case)
     - RCP 4.5: Moderate mitigation
     - RCP 6.0: Medium-high emissions
     - RCP 8.5: High emissions (worst case)
   
   - **Return Periods**: Select multiple (10, 25, 50, 100, 250 years)

3. **Run Analysis**
   - Click "Run CLIMADA Analysis"
   - Wait for data loading (3-5 seconds)

4. **View Results**
   
   **Flood Hazard Metrics:**
   - Flood depth for each return period
   - Annual probability values
   - Interactive return period curve

   **Scenario Comparison:**
   - Compare flood intensity across all RCP scenarios
   - View percentage changes from historical baseline
   - Identify worst-case and best-case futures

   **Financial Risk:**
   - Total exposure value
   - Expected Annual Impact (EAI)
   - EAI/Exposure ratio
   - Interpretation guidance

5. **Generate Report**
   - Click "Generate Full Report"
   - View comprehensive text report
   - Download for documentation

---

## Data Format Requirements

### CSV Upload Format

Your CSV file should have these columns:

```csv
date,rainfall
2020-01-01,25.5
2020-01-02,0.0
2020-01-03,45.2
2020-01-04,150.8
...
```

**Requirements:**
- `date`: YYYY-MM-DD format
- `rainfall`: Numeric values in millimeters
- Minimum: 365 days (1 year)
- Recommended: 1825+ days (5+ years)
- No missing values in critical columns

### Sample Data Format

When using "Generate Sample Data", the app creates realistic synthetic data with:
- Daily rainfall values (0-400mm)
- Seasonal patterns (monsoons)
- Extreme events
- Regional variations

---

## Understanding the Metrics

### Probability
**What it means:** Chance of an event occurring within the time window

**Example:** 
- 30-day flood probability of 5% = 1 in 20 chance of flood in next month
- 365-day flood probability of 50% = 1 in 2 chance of flood this year

**Risk Levels:**
- 🟢 Low: < 10%
- 🟡 Medium: 10-30%
- 🔴 High: > 30%

### Return Period
**What it means:** Average time between events of a given magnitude

**Example:**
- 100-year flood = 1% annual probability
- Doesn't mean it only happens once per century
- Can occur multiple times in short period or not at all for long period

**Common Return Periods:**
- 10 years: Frequent events, minor damage
- 50 years: Moderate events, building code standard
- 100 years: Major events, critical infrastructure design
- 250+ years: Extreme events, dam design

### Expected Annual Impact (EAI)
**What it means:** Average annual financial loss from floods

**Formula:** Sum of (Probability × Impact) for all return periods

**Example:**
- EAI = $100M, Exposure = $10B
- EAI/Exposure = 1%
- On average, lose 1% of assets per year to floods
- Over 10 years, expect ~$1B in damages

**Interpretation:**
- < 0.1%: Very low risk
- 0.1-1%: Low to moderate risk
- 1-5%: High risk
- > 5%: Very high risk

### Climate Scenarios (RCP)
**What they mean:** Different possible futures based on greenhouse gas emissions

| Scenario | Emissions | Temp Rise by 2100 | Likelihood |
|----------|-----------|-------------------|------------|
| RCP 2.6 | Very Low | +1.0 to +2.6°C | Requires strong action |
| RCP 4.5 | Moderate | +1.7 to +3.2°C | Possible with effort |
| RCP 6.0 | High | +2.0 to +3.7°C | Business as usual |
| RCP 8.5 | Very High | +3.2 to +5.4°C | Worst case |

**Impact on Floods:**
- Higher temperatures = more evaporation
- More moisture = heavier rainfall
- RCP 8.5 may show 50-100% increase in extreme rainfall
- Coastal flooding increases with sea level rise

---

## Visualization Guide

### Time Series Plot
**Shows:** Daily rainfall over time

**Features:**
- Hover for exact values
- Zoom: Click and drag
- Pan: Hold shift and drag
- Reset: Double-click
- Threshold lines show flood levels

**Interpretation:**
- Spikes above 150mm (red line) = flood events
- Clusters indicate wet periods
- Gaps indicate dry seasons

### Probability Bar Chart
**Shows:** Event probabilities for selected time window

**Color Coding:**
- Red: Extreme Rainfall (200mm+)
- Teal: Heavy Rainfall (100mm+)
- Blue: Flood events (150mm+)

**Use:** Compare risk levels across event types

### Return Period Curve
**Shows:** Flood intensity vs frequency

**Features:**
- Log scale X-axis (return period)
- Linear Y-axis (flood depth)
- Exponential relationship

**Interpretation:**
- Steeper curve = rapidly increasing risk
- Flatter curve = more gradual increase
- Extrapolate to estimate rare events

### Scenario Comparison
**Shows:** Climate scenario impacts

**Color Coding:**
- Gray: Historical baseline
- Green: RCP 2.6 (best case)
- Orange: RCP 4.5
- Orange-red: RCP 6.0
- Red: RCP 8.5 (worst case)

**Interpretation:**
- Higher bars = worse flooding
- Compare % changes from baseline
- Plan for range of futures

---

## Tips & Best Practices

### Data Quality
✅ **Do:**
- Use at least 5 years of daily data
- Ensure no large gaps in records
- Validate extreme values
- Check for data entry errors

❌ **Avoid:**
- Using incomplete years
- Mixing different measurement units
- Including erroneous spikes
- Insufficient data for trends

### Analysis Setup
✅ **Do:**
- Start with historical scenario for baseline
- Compare multiple return periods
- Consider seasonal patterns
- Validate results against known events

❌ **Avoid:**
- Relying on single scenario
- Ignoring confidence intervals
- Over-interpreting short-term data
- Extrapolating beyond data range

### Interpretation
✅ **Do:**
- Combine with local knowledge
- Consider multiple scenarios
- Account for model uncertainty
- Use for strategic planning

❌ **Avoid:**
- Treating probabilities as certainties
- Ignoring local conditions
- Over-relying on worst-case
- Making critical decisions on single metric

---

## Troubleshooting

### Issue: App won't start

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Slow performance

**Causes:**
- Large datasets (>10 years)
- Multiple simultaneous analyses
- Limited memory

**Solutions:**
- Reduce data size
- Close other browser tabs
- Restart app

### Issue: Upload fails

**Causes:**
- Wrong file format
- Missing columns
- Invalid dates

**Solutions:**
- Check CSV format matches requirements
- Ensure date column is YYYY-MM-DD
- Remove special characters
- Check for empty cells

### Issue: Charts not displaying

**Causes:**
- Browser compatibility
- Ad blockers
- JavaScript disabled

**Solutions:**
- Use modern browser (Chrome, Firefox, Edge)
- Disable ad blockers for app
- Enable JavaScript
- Clear browser cache

### Issue: Probabilities seem wrong

**Causes:**
- Insufficient data
- Seasonal bias
- Data quality issues

**Solutions:**
- Use minimum 5 years of data
- Check for missing periods
- Validate input data
- Compare with historical events

---

## Advanced Features

### Custom Analysis
You can modify the app to add:
- Additional locations
- Custom thresholds
- New event types
- Different time aggregations

**How to:**
1. Edit `webapp.py`
2. Modify event definitions
3. Update visualizations
4. Test thoroughly

### Batch Processing
For multiple locations:
1. Use Python script instead of web app
2. Import analyzer modules directly
3. Loop through locations
4. Export results to CSV

### API Integration
Connect to real-time data:
1. Add data source connectors
2. Implement automatic updates
3. Create alerts/notifications
4. Enable scheduled analysis

---

## Performance Optimization

### For Large Datasets
```python
# Use sampling for visualization
sampled_data = data.sample(frac=0.1)  # 10% sample

# Aggregate to monthly
monthly_data = data.resample('M').agg({'rainfall': 'sum'})
```

### For Multiple Users
- Deploy on cloud platform (AWS, Azure, GCP)
- Use caching (`@st.cache_data`)
- Implement session state
- Consider load balancing

### For Production
```bash
# Use production server
gunicorn app:server --workers 4

# Enable caching
streamlit run webapp.py --server.enableStaticServing true

# Set memory limits
streamlit run webapp.py --server.maxUploadSize 200
```

---

## Deployment Options

### Local Development
```bash
streamlit run webapp.py
```

### Network Access
```bash
streamlit run webapp.py --server.address 0.0.0.0 --server.port 8501
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "webapp.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### Cloud Platforms

**Streamlit Cloud:**
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

**Heroku:**
```bash
heroku create malaysia-climate-risk
git push heroku main
```

**AWS/Azure/GCP:**
- Use container services
- Configure load balancer
- Set up auto-scaling

---

## Security Considerations

### Data Privacy
- ⚠️ Don't upload sensitive data to public deployments
- ✅ Use local deployment for confidential data
- ✅ Implement authentication if needed
- ✅ Use HTTPS for production

### Access Control
```python
# Add password protection
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    'cookie_name',
    'signature_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')
```

---

## Support & Resources

### Documentation
- **CLIMADA Integration**: See `CLIMADA_INTEGRATION.md`
- **Main README**: See `README.md`
- **Code Documentation**: Inline comments in source files

### Help
- **Issues**: Open GitHub issue
- **Questions**: Contact development team
- **Streamlit Docs**: https://docs.streamlit.io/

### Citation
If using this tool in research or reports:

```
Malaysia Climate Risk Assessment Platform (2025)
CLIMADA Framework Integration
GitHub: github.com/edkp-2025/Team1
```

---

## Changelog

### Version 2.0 (Current)
- ✨ Added CLIMADA framework integration
- ✨ Interactive web application
- ✨ Multiple visualization types
- ✨ Scenario comparison tools
- ✨ Downloadable reports

### Version 1.0
- Basic probability calculations
- Seasonal analysis
- Trend predictions
- CSV data support

---

## Future Enhancements

Planned features:
- 🗺️ Interactive maps with flood zones
- 📧 Email alerts for high-risk periods
- 📱 Mobile-responsive design
- 🔄 Real-time data integration
- 🤖 Machine learning predictions
- 📊 More chart types
- 🌐 Multi-language support

---

## FAQ

**Q: Can I use this for property assessment?**
A: The tool provides regional risk estimates. For property-level assessment, combine with local surveys and expert evaluation.

**Q: How accurate are the predictions?**
A: Accuracy depends on data quality and quantity. Use 10+ years of data for best results. Validate against historical events.

**Q: What's the difference between modules?**
A: Quick Analysis uses your historical data for simple calculations. CLIMADA uses global datasets for professional risk assessment with climate scenarios.

**Q: Can I add my own locations?**
A: Yes! Edit `webapp.py` and add locations to the selection list. CLIMADA module needs corresponding hazard data.

**Q: Is this suitable for academic research?**
A: Yes, the CLIMADA module uses peer-reviewed methodologies. Cite appropriately and validate results.

**Q: How do I interpret conflicting scenarios?**
A: Use a range of scenarios for planning. Prepare for worst-case while working toward best-case through mitigation.

---

## Contact

For questions, issues, or contributions:
- **GitHub**: github.com/edkp-2025/Team1
- **Email**: [Your contact]
- **Documentation**: See repository README

---

**Ready to analyze climate risks?**

```bash
streamlit run webapp.py
```

Then navigate to `http://localhost:8501` in your browser!
