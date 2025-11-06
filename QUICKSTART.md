# Quick Start Guide - Malaysia Climate Event Probability

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage in 3 Steps

### Step 1: Import the Module

```python
from climate_probability import calculate_climate_event_probability
import pandas as pd
```

### Step 2: Prepare Your Data

```python
# Your data should have these columns:
data = pd.DataFrame({
    'date': pd.date_range('2015-01-01', '2024-12-31', freq='D'),
    'rainfall': [25.4, 150.2, 5.1, ...],      # mm per day
    'temperature': [28.5, 27.8, 29.2, ...]    # degrees Celsius
})
```

### Step 3: Calculate Probability

```python
# Calculate flood probability for next year
probability = calculate_climate_event_probability(data, 'flood', 365)
print(f"Flood probability: {probability:.2%}")
```

## Common Use Cases

### 1. Calculate Multiple Event Probabilities

```python
from climate_probability import ClimateEventAnalyzer

analyzer = ClimateEventAnalyzer(data)
probabilities = analyzer.calculate_all_probabilities(365)

for event, prob in probabilities.items():
    print(f"{event}: {prob:.2%}")
```

### 2. Seasonal Risk Analysis

```python
# Check flood risk during monsoon season
monsoon_risk = analyzer.get_seasonal_probability('flood', 'northeast_monsoon')
print(f"Flood risk during NE monsoon: {monsoon_risk:.2%}")
```

### 3. Predict Future Trends

```python
# Predict flood trends for next 5 years
trend = analyzer.predict_trend('flood', years_ahead=5)
print(f"Trend: {trend['trend']}")
print(f"Future probability: {trend['predicted_probability']:.2%}")
```

### 4. Test with Sample Data

```python
from climate_probability import generate_sample_data

# Generate 10 years of sample data
test_data = generate_sample_data(years=10, location='peninsular')
analyzer = ClimateEventAnalyzer(test_data)
```

## Event Types Available

- `'flood'` - Heavy flooding (≥150mm/24h)
- `'heavy_rainfall'` - Heavy rain (≥100mm/day)
- `'extreme_rainfall'` - Extreme rain (≥200mm/day)
- `'heatwave'` - Hot days (≥35°C)
- `'drought'` - Dry periods (14+ days <1mm rain)

## Monsoon Seasons

- `'northeast_monsoon'` - Nov-Mar (wet)
- `'southwest_monsoon'` - May-Sep (dry)
- `'inter_monsoon'` - Apr, Oct (transition)

## Running Examples

```bash
# Run built-in demo
python climate_probability.py

# Run all examples
python example_usage.py

# Run tests
python test_climate_probability.py
```

## Quick Tips

1. **More data = better accuracy**: Use at least 5-10 years of historical data
2. **Check data quality**: Ensure no missing dates or invalid values
3. **Regional differences**: Use location-specific data when possible
4. **Validate results**: Compare with official meteorological data
5. **Update regularly**: Recalculate probabilities with new data

## Troubleshooting

**Problem**: Low confidence in predictions
- **Solution**: Add more years of historical data

**Problem**: Probability is 100%
- **Solution**: May indicate extreme events are common; check your thresholds

**Problem**: Seasonal analysis returns 0%
- **Solution**: Ensure your data covers multiple years of that season

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [example_usage.py](example_usage.py) for comprehensive examples
- Check [climate_probability.py](climate_probability.py) for API details

## Need Help?

- Review the example scripts
- Check the API documentation in README.md
- Run the test suite to verify installation
- Open an issue in the repository

---

**Remember**: This tool is for analysis and research. For critical decisions, consult professional meteorologists and official sources!
