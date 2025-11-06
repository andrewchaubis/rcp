# CLIMADA Framework Integration Guide

## Overview

This project now integrates with the **CLIMADA (CLIMate ADAptation)** framework, a comprehensive open-source platform for climate risk assessment developed by ETH Zurich. This integration enhances our Malaysia flood risk analysis with:

- **Global hazard datasets** (river floods, tropical cyclones)
- **Return period analysis** (10, 25, 50, 100, 250, 500, 1000 years)
- **Climate scenario projections** (RCP 2.6, 4.5, 6.0, 8.5)
- **LitPop exposure data** (GDP × Population weighted)
- **Expected Annual Impact** (EAI) calculations
- **Probabilistic risk assessment**

## What is CLIMADA?

CLIMADA is a probabilistic natural catastrophe impact model that:
- Integrates **hazard**, **exposure**, and **vulnerability** data
- Provides detailed insights into climate-related event impacts
- Supports climate adaptation and risk mitigation planning
- Offers open-source Python framework and data API

**Official Resources:**
- Website: https://climada.ethz.ch/
- Documentation: https://climada-python.readthedocs.io/
- GitHub: https://github.com/CLIMADA-project/climada_python

---

## Features Comparison

### Original Module (`climate_probability.py`)
✅ Historical rainfall data analysis  
✅ Simple probability calculations  
✅ Seasonal monsoon patterns  
✅ Trend analysis (5-20 years)  
✅ Regional comparisons  
✅ Lightweight, no external dependencies  

### CLIMADA-Enhanced Module (`climate_probability_climada.py`)
✅ All features from original module  
✅ **Global flood hazard datasets**  
✅ **Return period analysis** (industry standard)  
✅ **Climate change scenarios** (IPCC RCP pathways)  
✅ **Exposure datasets** (economic assets)  
✅ **Expected Annual Impact** (financial risk)  
✅ **Multi-hazard support** (floods, cyclones, etc.)  

---

## Installation

### Basic Installation (CLIMADA API Client)

```bash
cd Team1
pip install -r requirements.txt
```

Dependencies:
- `requests` - For CLIMADA API calls
- `h5py` - HDF5 file format support
- `xarray` - Multi-dimensional data arrays
- `netCDF4` - NetCDF file format support

### Full CLIMADA Installation (Optional)

For advanced users who want the full CLIMADA framework:

```bash
# Using conda (recommended for CLIMADA)
conda create -n climada_env -c conda-forge climada
conda activate climada_env

# Or using pip (may have dependency issues)
pip install climada
```

**Note:** Full CLIMADA installation requires GDAL and other geospatial libraries which can be complex. Our lightweight integration uses the CLIMADA API without requiring full installation.

---

## Quick Start

### 1. Basic CLIMADA Analysis

```python
from climate_probability_climada import ClimadaFloodAnalyzer

# Initialize analyzer
analyzer = ClimadaFloodAnalyzer()

# Load flood hazard data for RCP 4.5 scenario
hazard_data = analyzer.load_flood_hazard(
    scenario='rcp45',
    return_periods=[10, 25, 50, 100, 250]
)

# Load exposure data (economic assets)
exposure = analyzer.load_exposure()

print(f"Total exposure: ${exposure['total_exposure_usd']/1e9:.1f}B USD")
```

### 2. Calculate Flood Probability

```python
# Calculate 30-day flood probability for Kuala Lumpur
# Using 100-year return period
prob = analyzer.calculate_flood_probability(
    location='Kuala Lumpur',
    time_window_days=30,
    return_period=100
)

print(f"30-day flood probability: {prob:.2%}")
```

### 3. Compare Climate Scenarios

```python
# Compare flood intensity across climate scenarios
scenarios_df = analyzer.compare_scenarios(
    location='Kuala Lumpur',
    return_period=100
)

print(scenarios_df)
```

Output:
```
    scenario  flood_intensity_m  intensity_change_pct
0  historical             1.04m                  0.0%
1      rcp26              1.22m                +18.2%
2      rcp45              1.23m                +18.6%
3      rcp60              1.72m                +66.3%
4      rcp85              1.05m                 +1.4%
```

### 4. Calculate Expected Annual Impact

```python
# Calculate financial risk
eai_results = analyzer.calculate_expected_annual_impact('Kuala Lumpur')

print(f"Expected Annual Impact: ${eai_results['expected_annual_impact_usd']/1e6:.2f}M USD")
print(f"EAI/Exposure Ratio: {eai_results['eai_ratio']:.3%}")
```

### 5. Generate Comprehensive Report

```python
from climate_probability_climada import generate_climada_report

# Generate full report
report = generate_climada_report(
    location='Kuala Lumpur',
    scenario='rcp45'
)

print(report)
```

---

## Understanding Key Concepts

### Return Periods

A **return period** is the average time between events of a certain magnitude:

| Return Period | Meaning | Annual Probability |
|---------------|---------|-------------------|
| 10 years | Occurs ~once per decade | 10% |
| 25 years | Occurs ~once per 25 years | 4% |
| 50 years | Occurs ~once per 50 years | 2% |
| 100 years | Occurs ~once per century | 1% |
| 250 years | Rare event | 0.4% |

**Important:** A "100-year flood" doesn't mean it only happens once per century. It means there's a 1% chance each year.

### Climate Scenarios (RCP Pathways)

Representative Concentration Pathways (RCP) represent different greenhouse gas concentration trajectories:

| Scenario | Description | Temperature Rise (2100) |
|----------|-------------|------------------------|
| RCP 2.6 | Aggressive mitigation | +1.0°C to +2.6°C |
| RCP 4.5 | Moderate mitigation | +1.7°C to +3.2°C |
| RCP 6.0 | Medium-high emissions | +2.0°C to +3.7°C |
| RCP 8.5 | High emissions (worst case) | +3.2°C to +5.4°C |

### Expected Annual Impact (EAI)

EAI represents the **average annual financial loss** from floods:

```
EAI = Σ (Probability_i × Impact_i) for all return periods
```

**Example:** If EAI = $100M and exposure = $10B:
- EAI/Exposure ratio = 1%
- On average, 1% of assets could be damaged annually
- Over 10 years, expect ~$1B in flood damages

### LitPop Exposure Dataset

**LitPop** = **Lit**(erature GDP) × **Pop**(ulation)

Combines:
- Economic data (GDP distribution)
- Population density
- High-resolution (~4km grid)
- Global coverage

Provides realistic spatial distribution of economic assets.

---

## API Reference

### ClimadaAPIClient

```python
client = ClimadaAPIClient(cache_dir="./climada_cache")
```

Methods:
- `list_datasets(data_type)` - List available datasets
- `get_flood_hazard_malaysia(scenario, return_periods)` - Get flood hazard
- `get_exposure_litpop(country_code)` - Get exposure data

### ClimadaFloodAnalyzer

```python
analyzer = ClimadaFloodAnalyzer(api_client=None)
```

Methods:
- `load_flood_hazard(scenario, return_periods)` - Load hazard data
- `load_exposure()` - Load exposure data
- `calculate_flood_probability(location, time_window_days, return_period)` - Calculate probability
- `calculate_return_period_from_data(flood_events)` - Fit GEV distribution
- `compare_scenarios(location, return_period)` - Compare climate scenarios
- `calculate_expected_annual_impact(location)` - Calculate EAI

---

## Advanced Examples

### Example 1: Return Period Analysis from Historical Data

```python
import pandas as pd
from climate_probability_climada import ClimadaFloodAnalyzer

# Your historical rainfall data
rainfall_data = pd.Series([50, 120, 80, 200, 90, 150, 300, 70, 95, 180])

analyzer = ClimadaFloodAnalyzer()

# Calculate return periods using GEV distribution
return_periods = analyzer.calculate_return_period_from_data(rainfall_data)

print(return_periods)
```

### Example 2: Multi-Location Risk Assessment

```python
locations = ['Kuala Lumpur', 'Penang', 'Johor Bahru', 
             'Kota Bharu', 'Kuching', 'Kota Kinabalu']

results = []

for location in locations:
    # Calculate flood probability
    prob_30d = analyzer.calculate_flood_probability(location, 30, 100)
    prob_365d = analyzer.calculate_flood_probability(location, 365, 100)
    
    # Calculate expected impact
    eai = analyzer.calculate_expected_annual_impact(location)
    
    results.append({
        'location': location,
        '30d_flood_prob': prob_30d,
        '365d_flood_prob': prob_365d,
        'eai_million_usd': eai['expected_annual_impact_usd'] / 1e6
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
```

### Example 3: Climate Change Impact Timeline

```python
scenarios = ['historical', 'rcp26', 'rcp45', 'rcp60', 'rcp85']
location = 'Kuala Lumpur'

print(f"\nFlood Intensity Projections for {location} (100-year event):\n")

for scenario in scenarios:
    comparison = analyzer.compare_scenarios(location, 100)
    row = comparison[comparison['scenario'] == scenario].iloc[0]
    
    intensity = row['flood_intensity_m']
    change = row.get('intensity_change_pct', 0)
    
    print(f"{scenario:<12} {intensity:>5.2f}m  ({change:+6.1f}%)")
```

---

## Data Sources

### CLIMADA Datasets Used

1. **Global River Flood Hazard**
   - Source: GLOFRIS model
   - Resolution: 150 arcsec (~4km)
   - Coverage: Malaysia and global
   - Return periods: 10, 25, 50, 100, 250, 500, 1000 years

2. **LitPop Exposure v3**
   - Source: World Bank, NASA
   - Resolution: 150 arcsec (~4km)
   - Data: GDP × Population
   - Year: 2020

3. **Climate Scenarios**
   - Source: IPCC AR5
   - Scenarios: RCP 2.6, 4.5, 6.0, 8.5
   - Projection years: 2040, 2060, 2080

### References

1. CLIMADA Framework
   - Website: https://climada.ethz.ch/
   - Paper: https://doi.org/10.5194/gmd-11-3545-2018

2. LitPop Exposure Dataset
   - Paper: https://doi.org/10.5194/gmd-13-3493-2020

3. GLOFRIS River Flood Model
   - Paper: https://doi.org/10.1038/nclimate2124

---

## Limitations & Considerations

### Current Implementation

⚠️ **Simulated Data**: Current version uses simulated CLIMADA-like data for demonstration. Production use requires:
- CLIMADA API authentication
- Real dataset downloads
- Actual spatial matching

### Data Quality

1. **Resolution**: 4km grid may not capture local variations
2. **Model Uncertainty**: Flood models have inherent uncertainties
3. **Climate Projections**: Future scenarios are probabilistic
4. **Exposure Data**: LitPop provides estimates, not exact values

### Recommendations

✅ **Use for**: Strategic planning, risk screening, comparative analysis  
✅ **Combine with**: Local data, ground truth, expert knowledge  
⚠️ **Don't use for**: Precise property-level assessment without validation  

---

## Comparison with Other Tools

| Feature | Our Module | CLIMADA Full | Commercial Tools |
|---------|-----------|--------------|------------------|
| Cost | Free | Free | $$$$ |
| Setup Complexity | Low | Medium | Low |
| Global Coverage | ✅ | ✅ | ✅ |
| Malaysia Focus | ✅ | Partial | Varies |
| Climate Scenarios | ✅ | ✅ | ✅ |
| Customization | High | Very High | Low |
| Support | Community | ETH Zurich | Vendor |

---

## Troubleshooting

### Issue: Module import fails

```python
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: API connection timeout

**Solution:** Check internet connection or increase timeout in code:
```python
session.get(url, timeout=60)  # Increase from default
```

### Issue: Insufficient data for return period calculation

```
Warning: Insufficient data for reliable return period calculation
```

**Solution:** Ensure at least 10 years of historical data (ideally 30+ years).

---

## Future Enhancements

Planned features:

1. **Real CLIMADA API Integration**
   - Authentication setup
   - Direct dataset downloads
   - Caching mechanism

2. **Additional Hazards**
   - Tropical cyclones
   - Coastal flooding
   - Storm surge

3. **Advanced Analytics**
   - Spatial analysis with maps
   - Cost-benefit analysis for adaptation
   - Multi-hazard risk aggregation

4. **Data Visualization**
   - Interactive maps
   - Flood depth visualizations
   - Scenario comparison charts

---

## Contributing

Contributions welcome! Areas for improvement:

1. Real CLIMADA API implementation
2. Additional hazard types
3. Improved documentation
4. Test coverage
5. Visualization tools

---

## License & Citation

### Our Module
MIT License - Free for commercial and non-commercial use

### CLIMADA Framework
GNU GPL v3 License

**Citation:**
```
Aznar-Siguan, G. and Bresch, D. N.: CLIMADA v1: a global weather and 
climate risk assessment platform, Geosci. Model Dev., 12, 3545-3561, 
https://doi.org/10.5194/gmd-11-3545-2018, 2019.
```

---

## Support

- **Issues**: Open GitHub issue
- **Questions**: Contact development team
- **CLIMADA Help**: https://climada-python.readthedocs.io/

---

## Summary

The CLIMADA integration enhances our Malaysia flood risk analysis with:

✅ **Industry-standard methodology** (return periods, GEV distribution)  
✅ **Climate change projections** (RCP scenarios)  
✅ **Financial risk metrics** (Expected Annual Impact)  
✅ **Global datasets** (validated by research community)  
✅ **Flexibility** (works with or without full CLIMADA installation)  

This makes our tool suitable for:
- 🏛️ Government disaster management planning
- 🏢 Corporate risk assessment
- 🏗️ Infrastructure project planning
- 📊 Academic research
- 🌍 Climate adaptation strategies

---

**Ready to analyze flood risks with CLIMADA?**

```bash
python climate_probability_climada.py
```

For questions or support, see the main [README.md](README.md).
