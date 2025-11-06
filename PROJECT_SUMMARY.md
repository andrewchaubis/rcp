# Project Summary: Climate Event Probability Analysis for Malaysia

## Overview

This project provides a comprehensive Python-based solution for analyzing historical rainfall data and determining the probability of flood and rainfall events in Malaysia. The module is designed for researchers, policymakers, disaster management teams, and anyone interested in understanding flood risks and rainfall patterns in Malaysia.

## What Has Been Created

### Core Module (`climate_probability.py`)
- **ClimateEventAnalyzer Class**: Main analysis engine with methods for:
  - Event probability calculation
  - Seasonal analysis
  - Trend prediction using statistical methods
  - Multi-event tracking
  
- **Helper Functions**:
  - `calculate_climate_event_probability()`: Simple interface for quick calculations
  - `generate_sample_data()`: Create synthetic data for testing and demos

### Key Features

1. **Multiple Climate Event Types**
   - Floods (≥150mm/24h)
   - Heavy Rainfall (≥100mm/day)
   - Extreme Rainfall (≥200mm/day)


2. **Flexible Time Windows**
   - Calculate probabilities for any time period (days, months, years)
   - Default: 365-day (1-year) window

3. **Seasonal Analysis**
   - Northeast Monsoon (Nov-Mar): Wet season
   - Southwest Monsoon (May-Sep): Dry season  
   - Inter-Monsoon (Apr, Oct): Transition periods

4. **Trend Prediction**
   - Linear regression-based forecasting
   - Confidence levels (high/medium/low)
   - Multi-year projections

5. **Regional Support**
   - Peninsular Malaysia
   - Sabah
   - Sarawak
   - Customizable for specific locations

## Files Included

| File | Purpose | Lines of Code |
|------|---------|--------------|
| `climate_probability.py` | Main module with all functionality | ~550 |
| `example_usage.py` | Comprehensive usage examples | ~280 |
| `test_climate_probability.py` | Test suite (10 tests, all passing) | ~260 |
| `requirements.txt` | Python dependencies | 3 |
| `README.md` | Full documentation | ~450 |
| `QUICKSTART.md` | Quick start guide | ~140 |
| `.gitignore` | Git ignore patterns | ~50 |

**Total**: ~1,730 lines of code and documentation

## Dependencies

- **numpy** (≥1.21.0): Numerical computations
- **pandas** (≥1.3.0): Data manipulation and time series
- **scipy** (≥1.7.0): Statistical analysis and regression

All dependencies are standard scientific Python libraries.

## Usage Examples

### Simple Usage
```python
from climate_probability import calculate_climate_event_probability, generate_sample_data

data = generate_sample_data(years=10, location='peninsular')
prob = calculate_climate_event_probability(data, 'flood', 365)
print(f"Flood probability: {prob:.2%}")
```

### Advanced Analysis
```python
from climate_probability import ClimateEventAnalyzer

analyzer = ClimateEventAnalyzer(historical_data)

# Get all probabilities
probs = analyzer.calculate_all_probabilities(365)

# Seasonal risk
monsoon_risk = analyzer.get_seasonal_probability('flood', 'northeast_monsoon')

# Future trends
trend = analyzer.predict_trend('flood', years_ahead=5)
```

## Statistical Methods

1. **Probability Calculation**
   - Uses complement probability: P(≥1 event) = 1 - (1-p)^n
   - Based on historical event frequency

2. **Trend Analysis**
   - Linear regression on yearly event counts
   - R-squared for confidence assessment
   - Future projections with uncertainty quantification

3. **Seasonal Decomposition**
   - Month-based filtering for monsoon seasons
   - Season-specific event counting

## Testing & Validation

✅ **10 Test Cases** - All Passing
- Sample data generation
- Basic probability calculation
- Analyzer initialization
- Multiple event probabilities
- Seasonal probability
- Trend prediction
- Different time windows
- Custom data handling
- Regional data processing
- Edge cases handling

## Potential Applications

1. **Disaster Management**
   - Flood risk assessment for emergency planning
   - Resource allocation for flood response
   - Early warning system development

2. **Agriculture**
   - Crop planning based on rainfall patterns
   - Irrigation planning
   - Flood risk for agricultural areas

3. **Infrastructure**
   - Flood risk assessment for construction
   - Urban planning and drainage systems
   - Climate-resilient infrastructure design

4. **Insurance**
   - Actuarial risk assessment
   - Premium calculation
   - Claims prediction

5. **Research**
   - Climate change impact studies
   - Long-term trend analysis
   - Regional climate comparisons

6. **Policy Making**
   - Climate adaptation strategies
   - Mitigation planning
   - Resource management policies

## Data Requirements

### Minimum Requirements
- **Date column**: Datetime format
- **Rainfall data**: Daily rainfall in mm
- **Recommended**: 5-10 years of daily data for reliable probabilities

### Optional Enhancements
- Pre-classified rainfall event types
- Multiple measurement locations
- Additional rainfall intensity data

## Limitations & Considerations

1. **Data Quality**: Accuracy depends on historical data quality
2. **Linear Assumptions**: Trend predictions assume linear relationships
3. **Climate Change**: May not capture non-linear climate change effects
4. **Local Variations**: Thresholds are generalized for Malaysia
5. **Synthetic Data**: Generated samples are for demonstration only

## Future Enhancements

Potential areas for expansion:
- Machine learning models (LSTM, Random Forest)
- Spatial analysis with GIS integration
- Real-time data integration from APIs
- Advanced climate indices (SOI, IOD, ENSO)
- Multi-variate analysis
- Extreme value theory implementation
- Climate change scenario modeling

## How to Get Started

1. **Installation**
   ```bash
   cd Team1
   pip install -r requirements.txt
   ```

2. **Run Examples**
   ```bash
   python climate_probability.py      # Basic demo
   python example_usage.py            # All examples
   python test_climate_probability.py # Run tests
   ```

3. **Use in Your Project**
   ```python
   from climate_probability import ClimateEventAnalyzer
   # Your code here...
   ```

4. **Read Documentation**
   - Quick start: `QUICKSTART.md`
   - Full docs: `README.md`
   - Examples: `example_usage.py`

## Git Repository

- **Branch**: `feature/probability`
- **Commits**: 2 commits with comprehensive changes
- **Status**: Clean working directory, ready for merge/review

## Quality Metrics

- ✅ All tests passing (10/10)
- ✅ Clean code with docstrings
- ✅ Comprehensive documentation
- ✅ Working examples included
- ✅ Git repository clean
- ✅ Dependencies minimal and standard

## Conclusion

This project delivers a production-ready, well-documented, and thoroughly tested Python module for climate event probability analysis specific to Malaysia. It provides both simple interfaces for quick use and advanced features for detailed analysis, making it suitable for a wide range of applications from academic research to operational risk management.

The module is designed to be:
- **Easy to use**: Simple function calls for basic needs
- **Powerful**: Advanced features for detailed analysis
- **Flexible**: Works with various data formats and time periods
- **Reliable**: Thoroughly tested and validated
- **Well-documented**: Multiple levels of documentation
- **Maintainable**: Clean code structure and comprehensive comments

---

**Created**: November 2025  
**Branch**: feature/probability  
**Repository**: edkp-2025/Team1  
**Status**: ✅ Ready for use
