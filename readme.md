# Flood Damage Calculation Library with JRC Data

A comprehensive Python library for calculating economic damages caused by floods, based on global damage functions from the **Joint Research Centre (JRC)** of the European Commission.

## 🌟 Key Features

### ✅ JRC Global Damage Functions
- **270 damage functions** processed from JRC (2017)
- **7 geographic regions**: Europe, North America, Central & South America, Asia, Africa, Oceania, Global
- **6 building types**: Residential, Commercial, Industrial, Transport, Infrastructure, Agriculture
- **9 flood depths**: 0.0 to 6.0 meters

### ✅ Maximum Damage Values by Country
- **248 countries** with specific data
- Values differentiated by building type
- Economic data in EUR (2010 base)
- Automatic adjustments by economic context

### ✅ Uncertainty Analysis
- JRC standard deviations
- Confidence intervals (68% and 95%)
- Sensitivity analysis

### ✅ Advanced Features
- Automatic region inference from coordinates
- Batch calculations for multiple locations
- ISO country code support
- Complete input data validation

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd flood_damage_library

# Install dependencies
pip install -r requirements.txt

# Process JRC data (required)
python process_jrc_excel.py
```

## 🚀 Quick Start

### Basic Calculation

```python
from flood_damage_library import JRCFloodDamageCalculator

# Initialize calculator
calculator = JRCFloodDamageCalculator(data_directory="./processed_jrc_data")

# Option 1: Simple calculation with country code (coordinates optional!)
result = calculator.calculate_damage_by_country(
    flood_depth=1.5,       # 1.5 meters
    country_code='DE',     # Germany
    building_type='residential',
    area_m2=120           # 120 m²
)

# Option 2: With coordinates (for automatic country inference)
result = calculator.calculate_jrc_damage(
    latitude=52.5200,      # Berlin coordinates
    longitude=13.4050,
    flood_depth=1.5,
    building_type='residential',
    area_m2=120
)

print(f"Economic damage: €{result['damage_assessment']['economic_damage_eur']:,.2f}")
print(f"Damage ratio: {result['damage_assessment']['damage_ratio']:.1%}")
```

### Batch Analysis

```python
# Multiple locations
locations = [
    {
        'latitude': 52.5200, 'longitude': 13.4050, 'flood_depth': 1.5,
        'country_code': 'DE', 'building_type': 'residential', 'area_m2': 100
    },
    {
        'latitude': 48.8566, 'longitude': 2.3522, 'flood_depth': 2.0,
        'country_code': 'FR', 'building_type': 'commercial', 'area_m2': 150
    }
]

results = calculator.calculate_damage_batch_jrc(locations)

total_damage = sum(r['damage_assessment']['economic_damage_eur'] 
                  for r in results if 'error' not in r)
print(f"Total damage: €{total_damage:,.2f}")
```

### Batch Analysis by Country (No Coordinates Required)

```python
# Portfolio analysis using only country codes
scenarios = [
    {
        'flood_depth': 1.5, 'country_code': 'DE', 
        'building_type': 'residential', 'area_m2': 120
    },
    {
        'flood_depth': 2.0, 'country_code': 'FR', 
        'building_type': 'commercial', 'area_m2': 500
    },
    {
        'flood_depth': 1.8, 'country_code': 'IT', 
        'building_type': 'industrial', 'area_m2': 1000
    }
]

# Process batch by country (no coordinates needed)
results = calculator.calculate_damage_batch_by_country(scenarios)

for result in results:
    if 'error' not in result:
        scenario = result['input_scenario']
        damage = result['damage_assessment']['economic_damage_eur']
        print(f"{scenario['country_code']} {scenario['building_type']}: €{damage:,.0f}")
```

## 📊 Data Structure

### Calculation Result

```python
{
    'location': {
        'latitude': 52.5200,
        'longitude': 13.4050,
        'country_code': 'DE',
        'country_name': 'GERMANY',
        'region': 'EUROPE'
    },
    'flood_parameters': {
        'depth_m': 1.5
    },
    'property_characteristics': {
        'building_type': 'residential',
        'area_m2': 120,
        'max_damage_per_m2_eur': 783.04,
        'total_value_eur': 93964.87,
        'currency': 'EUR',
        'base_year': 2010
    },
    'damage_assessment': {
        'damage_ratio': 0.50,
        'economic_damage_eur': 46982.44,
        'currency': 'EUR'
    },
    'uncertainty_analysis': {
        'standard_deviation_ratio': 0.20,
        'confidence_interval_95': {
            'lower_eur': 28565.46,
            'upper_eur': 65399.42
        }
    }
}
```

## 🌍 Supported Regions and Types

### JRC Regions
- **EUROPE**: Europe
- **North AMERICA**: North America
- **Centr&South_AMERICA**: Central and South America
- **ASIA**: Asia
- **AFRICA**: Africa
- **OCEANIA**: Oceania
- **GLOBAL**: Global function (average)

### Building Types
- **residential**: Residential buildings
- **commercial**: Commercial buildings
- **industrial**: Industrial buildings

### Countries with Data
248 countries included with specific maximum damage values.

## 🔧 Complete API

### JRCFloodDamageCalculator

#### Main Methods

```python
# Individual calculation (flexible - with or without coordinates)
calculate_jrc_damage(latitude=None, longitude=None, flood_depth=None, 
                    country_code=None, building_type='residential', 
                    area_m2=None, region=None)

# Simplified country-based calculation (no coordinates needed)
calculate_damage_by_country(flood_depth, country_code, 
                           building_type='residential', area_m2=None, region=None)

# Batch calculation (with coordinates)
calculate_damage_batch_jrc(locations)

# Batch calculation by country (no coordinates needed)
calculate_damage_batch_by_country(scenarios)

# Available information
get_available_regions()
get_available_building_types()
get_countries_with_data(building_type='residential')
```

#### Parameters

- **flood_depth** (float): Depth in meters (≥ 0) - **Required**
- **country_code** (str): ISO country code (e.g., 'US', 'DE', 'BR') - **Required if no coordinates**
- **latitude** (float, optional): Latitude (-90 to 90) - Only needed if country_code not provided
- **longitude** (float, optional): Longitude (-180 to 180) - Only needed if country_code not provided
- **building_type** (str): 'residential', 'commercial', 'industrial', 'agriculture', 'infrastructure', 'transport' - Default: 'residential'
- **area_m2** (float, optional): Area in square meters - Default: 100
- **region** (str, optional): Specific JRC region - Auto-inferred from country if not provided

**Note**: Either provide `country_code` OR both `latitude` and `longitude`. Coordinates are only used for automatic country inference.

## 📋 Data Validation

The library includes automatic validation for:

- ✅ Valid geographic coordinates
- ✅ Non-negative flood depths
- ✅ Supported building types
- ✅ Valid country codes
- ✅ Positive areas

## 🧪 Tests

```bash
# Run all tests
python -m pytest tests/ -v

# JRC-specific tests
python -m pytest tests/test_jrc_calculator.py -v

# Tests with coverage
python -m pytest tests/ --cov=flood_damage_library --cov-report=html
```

## 📚 Data Source

Data comes from:

**"Global flood depth-damage functions database"**
- Joint Research Centre (JRC), European Commission
- April 2017
- File: `copy_of_global_flood_depth-damage_functions__30102017.xlsx`

### Data Processing

```bash
# Process JRC Excel file
python process_jrc_excel.py

# Generated files:
# - processed_jrc_data/damage_functions_jrc.parquet
# - processed_jrc_data/max_damage_residential_jrc.parquet
# - processed_jrc_data/max_damage_commercial_jrc.parquet
# - processed_jrc_data/max_damage_industrial_jrc.parquet
# - processed_jrc_data/iso_table_jrc.parquet
```

## 🎯 Use Cases

### 1. Flood Risk Assessment
```python
# Evaluate multiple depth scenarios
scenarios = [0.5, 1.0, 1.5, 2.0, 3.0]
for depth in scenarios:
    result = calculator.calculate_jrc_damage(
        latitude=40.7128, longitude=-74.0060,  # New York
        flood_depth=depth,
        country_code='US',
        building_type='commercial',
        area_m2=500
    )
    print(f"Depth {depth}m: €{result['damage_assessment']['economic_damage_eur']:,.0f}")
```

### 2. Property Portfolio Analysis
```python
# Property portfolio
portfolio = [
    {'lat': 52.52, 'lon': 13.40, 'country': 'DE', 'type': 'residential', 'area': 120},
    {'lat': 48.86, 'lon': 2.35, 'country': 'FR', 'type': 'commercial', 'area': 200},
    {'lat': 41.90, 'lon': 12.50, 'country': 'IT', 'type': 'industrial', 'area': 800}
]

total_risk = 0
for prop in portfolio:
    result = calculator.calculate_jrc_damage(
        latitude=prop['lat'], longitude=prop['lon'],
        flood_depth=2.0,  # 2m scenario
        country_code=prop['country'],
        building_type=prop['type'],
        area_m2=prop['area']
    )
    total_risk += result['damage_assessment']['economic_damage_eur']

print(f"Total portfolio risk: €{total_risk:,.2f}")
```

## 🔍 Uncertainty Analysis

```python
# Detailed uncertainty analysis
result = calculator.calculate_jrc_damage(
    latitude=52.5200, longitude=13.4050,
    flood_depth=1.5, country_code='DE',
    building_type='residential', area_m2=100
)

uncertainty = result['uncertainty_analysis']
damage = result['damage_assessment']['economic_damage_eur']

print(f"Estimated damage: €{damage:,.2f}")
print(f"Standard deviation: {uncertainty['standard_deviation_ratio']:.1%}")

ci_95 = uncertainty['confidence_interval_95']
print(f"95% CI: €{ci_95['lower_eur']:,.0f} - €{ci_95['upper_eur']:,.0f}")
```

## 🚨 Limitations and Considerations

### Data Limitations
- JRC data is from 2017 and may not reflect current conditions
- Values are in EUR 2010 and may require inflation adjustments
- Some regions have limited data (especially Africa and Oceania)

### Usage Considerations
- Results are estimates based on average functions
- Validation with local data is recommended when possible
- Uncertainty can be significant (±20-40% typically)

### Recommendations
- Use multiple scenarios for sensitivity analysis
- Consider local factors not captured in global functions
- Update economic values according to local inflation

## 📁 Repository Structure

```
climate_risk_damage_function/
├── flood_damage_library/           # Main library package
│   ├── __init__.py
│   ├── core/                       # Core calculation modules
│   │   ├── __init__.py
│   │   ├── jrc_damage_calculator.py    # Main JRC calculator
│   │   ├── damage_calculator.py        # Base calculator
│   │   ├── data_manager.py             # Data management
│   │   └── enhanced_damage_calculator.py
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       ├── exceptions.py           # Custom exceptions
│       └── validators.py           # Input validation
├── processed_jrc_data/             # JRC data (8 parquet files)
│   ├── damage_functions_jrc.parquet     # 270 damage functions
│   ├── iso_table_jrc.parquet           # Country codes
│   ├── max_damage_residential_jrc.parquet
│   ├── max_damage_commercial_jrc.parquet
│   ├── max_damage_industrial_jrc.parquet
│   ├── max_damage_agriculture_jrc.parquet
│   ├── max_damage_infrastructure_jrc.parquet
│   └── max_damage_transport_jrc.parquet
├── flood_damage_tutorial.ipynb    # Interactive tutorial
├── requirements.txt               # Dependencies
├── setup.py                      # Package installation
└── README.md                     # Documentation
```

## 📄 License

This project is under MIT license. See `LICENSE` file for details.

## 🙏 Acknowledgments

- **Joint Research Centre (JRC)** of the European Commission for providing the global database
- Flood risk assessment scientific community
- Project contributors

---

**Version**: 2.0.0  
**Last updated**: November 2024  
**Compatibility**: Python 3.8+
# Climate Event Probability Analysis for Malaysia

A comprehensive Python module for analyzing historical climate data and determining the probability of major climate events in Malaysia, with **CLIMADA framework integration** for advanced flood risk assessment.

## 🆕 NEW: CLIMADA Integration

This project now includes integration with the **CLIMADA (CLIMate ADAptation)** framework from ETH Zurich, providing:
- 🌍 Global flood hazard datasets
- 📊 Return period analysis (10-1000 years)
- 🌡️ Climate scenario projections (RCP 2.6 - 8.5)
- 💰 Expected Annual Impact calculations
- 🏛️ LitPop exposure data for Malaysia

**See [CLIMADA_INTEGRATION.md](CLIMADA_INTEGRATION.md) for full details.**

## Two Modules Available

### 1. Original Module (`climate_probability.py`)
- Lightweight, minimal dependencies
- Historical rainfall data analysis
- Focus on floods and rainfall events only
- Seasonal monsoon patterns
- Trend predictions

### 2. CLIMADA-Enhanced Module (`climate_probability_climada.py`) ⭐ NEW
- Industry-standard risk assessment
- Global hazard datasets
- Return period analysis (10-1000 years)
- Climate change scenarios (RCP 2.6-8.5)
- Expected Annual Impact (EAI)
- Financial risk metrics

## Features

- 🌧️ **Multiple Event Types**: Analyze floods, droughts, heatwaves, heavy rainfall, and extreme rainfall events
- 📊 **Historical Analysis**: Process and analyze historical climate data with automatic event detection
- 🔮 **Probability Calculation**: Calculate event probabilities for custom time windows
- 🌏 **Seasonal Analysis**: Determine event probabilities during different monsoon seasons
- 📈 **Trend Prediction**: Predict future climate event trends using statistical analysis
- 🗺️ **Regional Support**: Optimized for different regions of Malaysia (Peninsular, Sabah, Sarawak)
- 📉 **Statistical Methods**: Uses robust statistical techniques including linear regression and probability theory

## Installation

### Requirements

**Basic (Original Module):**
- Python 3.7+
- numpy >= 1.21.0
- pandas >= 1.3.0
- scipy >= 1.7.0

**CLIMADA Integration (Additional):**
- requests >= 2.28.0
- h5py >= 3.8.0
- xarray >= 2023.0.0
- netCDF4 >= 1.6.0

### Install Dependencies

```bash
pip install -r requirements.txt
```

All dependencies (including CLIMADA integration) will be installed.

## Quick Start

### Basic Usage (Original Module)

```python
import pandas as pd
from climate_probability import calculate_climate_event_probability

# Load your historical climate data
data = pd.DataFrame({
    'date': pd.date_range('2015-01-01', '2024-12-31', freq='D'),
    'rainfall': [/* your rainfall data in mm */]
})

# Calculate flood probability for the next year
flood_probability = calculate_climate_event_probability(data, 'flood', 365)
print(f"Flood probability: {flood_probability:.2%}")
```

### CLIMADA-Enhanced Usage ⭐ NEW

```python
from climate_probability_climada import ClimadaFloodAnalyzer, generate_climada_report

# Initialize analyzer
analyzer = ClimadaFloodAnalyzer()

# Load CLIMADA hazard and exposure data
analyzer.load_flood_hazard(scenario='rcp45', return_periods=[10, 25, 50, 100])
analyzer.load_exposure()

# Calculate flood probability using return periods
prob = analyzer.calculate_flood_probability('Kuala Lumpur', time_window_days=30, return_period=100)
print(f"30-day flood probability: {prob:.2%}")

# Compare climate scenarios
scenarios = analyzer.compare_scenarios('Kuala Lumpur', return_period=100)
print(scenarios)

# Calculate Expected Annual Impact
eai = analyzer.calculate_expected_annual_impact('Kuala Lumpur')
print(f"Expected Annual Impact: ${eai['expected_annual_impact_usd']/1e6:.2f}M USD")

# Generate comprehensive report
report = generate_climada_report('Kuala Lumpur', 'rcp45')
print(report)
```

### Advanced Usage

```python
from climate_probability import ClimateEventAnalyzer

# Create analyzer instance
analyzer = ClimateEventAnalyzer(historical_data)

# Get all event probabilities
probabilities = analyzer.calculate_all_probabilities(time_window=365)
for event, prob in probabilities.items():
    print(f"{event}: {prob:.2%}")

# Seasonal analysis
flood_risk_monsoon = analyzer.get_seasonal_probability('flood', 'northeast_monsoon')
print(f"Flood risk during NE monsoon: {flood_risk_monsoon:.2%}")

# Trend prediction
trend_info = analyzer.predict_trend('flood', years_ahead=5)
print(f"Predicted trend: {trend_info['trend']}")
print(f"Future probability: {trend_info['predicted_probability']:.2%}")
```

## Climate Event Types

The module supports analysis of the following climate events:

| Event Type | Description | Threshold |
|------------|-------------|-----------|
| `flood` | Flooding events | ≥150 mm rainfall in 24 hours |
| `heavy_rainfall` | Heavy rainfall days | ≥100 mm per day |
| `extreme_rainfall` | Extreme rainfall events | ≥200 mm per day |
| `heatwave` | Heatwave days | Temperature ≥35°C |
| `drought` | Drought periods | 14+ consecutive days with <1mm rain |

## Data Format

Your historical data should be a pandas DataFrame with the following columns:

### Required Columns

- **date**: Date of observation (datetime format)

### Optional Columns

- **rainfall**: Daily rainfall in millimeters (float)
- **temperature**: Daily temperature in Celsius (float)
- **event_type**: Pre-classified event type (string)

### Example Data Structure

```python
data = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'rainfall': [25.4, 150.2, 5.1],
    'temperature': [28.5, 27.8, 29.2],
    'event_type': [None, 'flood', None]
})
```

## Monsoon Seasons in Malaysia

The module recognizes three main seasons:

- **Northeast Monsoon** (`northeast_monsoon`): November - March (wet season)
- **Southwest Monsoon** (`southwest_monsoon`): May - September (dry season)
- **Inter-Monsoon** (`inter_monsoon`): April, October (transition periods)

## API Reference

### `calculate_climate_event_probability()`

Main function for calculating event probability.

```python
calculate_climate_event_probability(
    historical_data: pd.DataFrame,
    event_type: str,
    time_window: int = 365
) -> float
```

**Parameters:**
- `historical_data`: DataFrame with climate data
- `event_type`: Type of event ('flood', 'drought', 'heavy_rainfall', etc.)
- `time_window`: Number of days for probability calculation (default: 365)

**Returns:** Probability value between 0 and 1

### `ClimateEventAnalyzer`

Class for comprehensive climate analysis.

#### Methods

**`__init__(historical_data)`**
- Initialize analyzer with historical data

**`calculate_event_probability(event_type, time_window)`**
- Calculate probability for a specific event

**`calculate_all_probabilities(time_window)`**
- Calculate probabilities for all detected events

**`get_seasonal_probability(event_type, season)`**
- Get probability during a specific season

**`predict_trend(event_type, years_ahead)`**
- Predict future trends for an event type

### `generate_sample_data()`

Generate synthetic climate data for testing.

```python
generate_sample_data(
    years: int = 10,
    location: str = 'peninsular'
) -> pd.DataFrame
```

**Parameters:**
- `years`: Number of years of data to generate
- `location`: Region ('peninsular', 'sabah', 'sarawak')

**Returns:** DataFrame with synthetic climate data

## Examples

### Example 1: Simple Probability Calculation

```python
from climate_probability import generate_sample_data, calculate_climate_event_probability

# Generate sample data
data = generate_sample_data(years=10, location='peninsular')

# Calculate probabilities
flood_prob = calculate_climate_event_probability(data, 'flood', 365)
drought_prob = calculate_climate_event_probability(data, 'drought', 365)

print(f"Annual flood probability: {flood_prob:.2%}")
print(f"Annual drought probability: {drought_prob:.2%}")
```

### Example 2: Seasonal Risk Assessment

```python
from climate_probability import ClimateEventAnalyzer, generate_sample_data

data = generate_sample_data(years=15)
analyzer = ClimateEventAnalyzer(data)

# Compare flood risk across seasons
seasons = ['northeast_monsoon', 'southwest_monsoon', 'inter_monsoon']
for season in seasons:
    prob = analyzer.get_seasonal_probability('flood', season)
    print(f"{season}: {prob:.2%}")
```

### Example 3: Trend Analysis

```python
from climate_probability import ClimateEventAnalyzer, generate_sample_data

data = generate_sample_data(years=20)
analyzer = ClimateEventAnalyzer(data)

# Analyze 10-year trend
trend_info = analyzer.predict_trend('heatwave', years_ahead=10)

print(f"Current probability: {trend_info['current_probability']:.2%}")
print(f"Predicted probability: {trend_info['predicted_probability']:.2%}")
print(f"Trend: {trend_info['trend']}")
print(f"Confidence: {trend_info['confidence']}")
```

### Example 4: Regional Comparison

```python
from climate_probability import ClimateEventAnalyzer, generate_sample_data

regions = ['peninsular', 'sabah', 'sarawak']

for region in regions:
    data = generate_sample_data(years=10, location=region)
    analyzer = ClimateEventAnalyzer(data)
    
    flood_prob = analyzer.calculate_event_probability('flood', 365)
    print(f"{region.title()}: {flood_prob:.2%}")
```

## Running Examples

The repository includes comprehensive example scripts:

```bash
# Run the main module with built-in examples
python climate_probability.py

# Run all example scenarios
python example_usage.py
```

## Climate Thresholds

The module uses the following thresholds based on Malaysian climate patterns:

```python
THRESHOLDS = {
    'heavy_rainfall': 100,      # mm per day
    'extreme_rainfall': 200,    # mm per day
    'drought_days': 14,         # consecutive days with < 1mm rain
    'heatwave_temp': 35,        # °C
    'flood_rainfall': 150,      # mm in 24 hours
}
```

These can be customized by modifying the `ClimateEventAnalyzer.THRESHOLDS` dictionary.

## Statistical Methods

### Probability Calculation

The module uses complement probability for time windows:

```
P(at least one event in N days) = 1 - (1 - p)^N
```

where `p` is the daily probability based on historical data.

### Trend Prediction

Linear regression is used for trend analysis:
- **Slope > 0.5**: Increasing trend
- **Slope < -0.5**: Decreasing trend
- **Otherwise**: Stable trend

Confidence levels are based on R-squared values:
- **High confidence**: R² > 0.7
- **Medium confidence**: R² > 0.4
- **Low confidence**: R² ≤ 0.4

## Use Cases

1. **Disaster Preparedness**: Assess flood and extreme weather risks for emergency planning
2. **Agricultural Planning**: Analyze drought and rainfall patterns for crop management
3. **Infrastructure Planning**: Evaluate climate risks for construction projects
4. **Insurance Risk Assessment**: Calculate event probabilities for actuarial analysis
5. **Climate Research**: Study long-term climate trends and patterns in Malaysia
6. **Policy Making**: Inform climate adaptation and mitigation strategies

## Limitations

- Requires historical data for accurate predictions
- Thresholds are generalized for Malaysia (may need adjustment for specific locations)
- Synthetic data is for demonstration purposes only
- Trend predictions assume linear relationships (may not capture complex climate patterns)
- Does not account for climate change acceleration or non-linear effects

## Data Sources

For real-world applications, consider using data from:

- **Malaysian Meteorological Department (MetMalaysia)**
- **Department of Irrigation and Drainage (DID)**
- **ASEAN Specialised Meteorological Centre (ASMC)**
- **Global Historical Climatology Network (GHCN)**
- **ERA5 Reanalysis Data (ECMWF)**

## Contributing

Contributions are welcome! Areas for improvement:

- Additional climate event types
- More sophisticated statistical models
- Machine learning integration
- Spatial analysis capabilities
- Real-time data integration

## License

This project is open source and available for educational and research purposes.

## Citation

If you use this module in your research, please cite:

```
Malaysia Climate Event Probability Analysis
Repository: edkp-2025/Team1
Branch: feature/probability
Year: 2025
```

## Contact

For questions, issues, or suggestions, please open an issue in the repository.

---

**Note**: This module is designed for analysis and research purposes. For critical decision-making, always consult with climate scientists and use official meteorological data sources.
