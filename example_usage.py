"""
Example usage of the climate event probability analysis functions.

This script demonstrates how to use the climate_probability module
with both synthetic and real data scenarios.
"""

import pandas as pd
import numpy as np
from climate_probability import (
    ClimateEventAnalyzer,
    calculate_climate_event_probability,
    generate_sample_data
)


def example_basic_usage():
    """Demonstrate basic usage with sample data."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage with Sample Data")
    print("="*70)
    
    # Generate sample data for Peninsular Malaysia
    data = generate_sample_data(years=10, location='peninsular')
    
    print(f"\nGenerated {len(data)} days of climate data")
    print("\nData Preview:")
    print(data.head(10))
    
    # Calculate probability using the simple function
    flood_prob = calculate_climate_event_probability(data, 'flood', 365)
    print(f"\n✓ Probability of flood in the next year: {flood_prob:.2%}")


def example_detailed_analysis():
    """Demonstrate detailed analysis with ClimateEventAnalyzer."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Detailed Analysis with ClimateEventAnalyzer")
    print("="*70)
    
    # Generate sample data
    data = generate_sample_data(years=15, location='peninsular')
    
    # Create analyzer instance
    analyzer = ClimateEventAnalyzer(data)
    
    # Get all probabilities
    print("\nAll Climate Event Probabilities (1-year window):")
    print("-"*70)
    probabilities = analyzer.calculate_all_probabilities(time_window=365)
    for event, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
        print(f"  {event.replace('_', ' ').title():.<40} {prob:.2%}")
    
    # Different time windows
    print("\n\nFlood Probability for Different Time Windows:")
    print("-"*70)
    for days in [30, 90, 180, 365]:
        prob = analyzer.calculate_event_probability('flood', days)
        print(f"  {days} days ({days/30:.1f} months):  {prob:.2%}")


def example_seasonal_analysis():
    """Demonstrate seasonal probability analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Seasonal Analysis")
    print("="*70)
    
    data = generate_sample_data(years=12, location='peninsular')
    analyzer = ClimateEventAnalyzer(data)
    
    print("\nSeasonal Flood Risk in Malaysia:")
    print("-"*70)
    
    seasons = {
        'northeast_monsoon': 'Northeast Monsoon (Nov-Mar) - Wet Season',
        'southwest_monsoon': 'Southwest Monsoon (May-Sep) - Dry Season',
        'inter_monsoon': 'Inter-Monsoon (Apr, Oct) - Transition'
    }
    
    for season_key, season_desc in seasons.items():
        prob = analyzer.get_seasonal_probability('flood', season_key)
        print(f"  {season_desc}")
        print(f"    → Flood Risk: {prob:.2%}\n")


def example_trend_prediction():
    """Demonstrate trend prediction functionality."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Climate Event Trend Prediction")
    print("="*70)
    
    data = generate_sample_data(years=20, location='peninsular')
    analyzer = ClimateEventAnalyzer(data)
    
    events = ['flood', 'heavy_rainfall', 'heatwave']
    
    for event in events:
        print(f"\n{event.replace('_', ' ').title()} - 10 Year Prediction:")
        print("-"*70)
        
        trend_info = analyzer.predict_trend(event, years_ahead=10)
        
        print(f"  Current Probability: {trend_info['current_probability']:.2%}")
        print(f"  Predicted Probability (10 years): {trend_info['predicted_probability']:.2%}")
        print(f"  Trend: {trend_info['trend'].upper()}")
        print(f"  Confidence: {trend_info['confidence'].upper()} (R² = {trend_info['r_squared']:.3f})")
        
        if trend_info['trend'] == 'increasing':
            print(f"  ⚠️  Warning: {event.replace('_', ' ').title()} events are increasing!")
        elif trend_info['trend'] == 'decreasing':
            print(f"  ✓ Good news: {event.replace('_', ' ').title()} events are decreasing.")


def example_regional_comparison():
    """Compare climate probabilities across different regions of Malaysia."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Regional Comparison")
    print("="*70)
    
    regions = ['peninsular', 'sabah', 'sarawak']
    results = {}
    
    for region in regions:
        data = generate_sample_data(years=10, location=region)
        analyzer = ClimateEventAnalyzer(data)
        results[region] = analyzer.calculate_all_probabilities(365)
    
    print("\nFlood Probability Comparison (1-year window):")
    print("-"*70)
    for region in regions:
        flood_prob = results[region].get('flood', 0)
        print(f"  {region.title():.<20} {flood_prob:.2%}")
    
    print("\n\nHeavy Rainfall Probability Comparison (1-year window):")
    print("-"*70)
    for region in regions:
        rain_prob = results[region].get('heavy_rainfall', 0)
        print(f"  {region.title():.<20} {rain_prob:.2%}")


def example_custom_data():
    """Demonstrate usage with custom historical data."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Using Custom Historical Data")
    print("="*70)
    
    # Create custom data (simulating real observations)
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')
    
    # Simulate realistic patterns
    np.random.seed(42)
    rainfall = np.random.gamma(2, 25, len(dates))
    temperature = np.random.normal(27, 2.5, len(dates))
    
    # Add some documented extreme events
    rainfall[100] = 250  # Extreme rainfall event
    rainfall[500] = 180  # Flood event
    rainfall[800] = 220  # Another extreme event
    
    custom_data = pd.DataFrame({
        'date': dates,
        'rainfall': rainfall,
        'temperature': temperature
    })
    
    print("\nCustom Data Summary:")
    print("-"*70)
    print(f"  Date Range: {custom_data['date'].min().date()} to {custom_data['date'].max().date()}")
    print(f"  Total Days: {len(custom_data)}")
    print(f"  Avg Rainfall: {custom_data['rainfall'].mean():.1f} mm/day")
    print(f"  Avg Temperature: {custom_data['temperature'].mean():.1f} °C")
    
    # Analyze
    analyzer = ClimateEventAnalyzer(custom_data)
    
    print("\n\nEvent Probabilities from Custom Data:")
    print("-"*70)
    probabilities = analyzer.calculate_all_probabilities(365)
    for event, prob in sorted(probabilities.items()):
        print(f"  {event.replace('_', ' ').title():.<40} {prob:.2%}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "MALAYSIA CLIMATE EVENT PROBABILITY ANALYSIS" + " "*15 + "║")
    print("║" + " "*22 + "Example Usage Demonstrations" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        example_basic_usage()
        example_detailed_analysis()
        example_seasonal_analysis()
        example_trend_prediction()
        example_regional_comparison()
        example_custom_data()
        
        print("\n\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        print("\nTo use this module in your own code:")
        print("  1. Import: from climate_probability import calculate_climate_event_probability")
        print("  2. Prepare your data with columns: date, rainfall, temperature")
        print("  3. Call: probability = calculate_climate_event_probability(data, 'flood', 365)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
