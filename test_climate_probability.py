"""
Simple tests for the climate probability module.
Run with: python test_climate_probability.py
"""

import pandas as pd
import numpy as np
from climate_probability import (
    ClimateEventAnalyzer,
    calculate_climate_event_probability,
    generate_sample_data
)


def test_generate_sample_data():
    """Test sample data generation."""
    print("Testing sample data generation...")
    
    data = generate_sample_data(years=5, location='peninsular')
    assert len(data) == 5 * 365, "Data should have 5 years of daily records"
    assert 'date' in data.columns, "Data should have date column"
    assert 'rainfall' in data.columns, "Data should have rainfall column"
    assert 'event_type' in data.columns, "Data should have event_type column"
    
    print("  ✓ Sample data generation works correctly")


def test_basic_probability_calculation():
    """Test basic probability calculation."""
    print("Testing basic probability calculation...")
    
    data = generate_sample_data(years=10)
    prob = calculate_climate_event_probability(data, 'flood', 365)
    
    assert 0 <= prob <= 1, "Probability should be between 0 and 1"
    assert isinstance(prob, float), "Probability should be a float"
    
    print(f"  ✓ Flood probability calculated: {prob:.2%}")


def test_analyzer_initialization():
    """Test ClimateEventAnalyzer initialization."""
    print("Testing analyzer initialization...")
    
    data = generate_sample_data(years=5)
    analyzer = ClimateEventAnalyzer(data)
    
    assert analyzer.total_days == len(data), "Total days should match data length"
    assert len(analyzer.event_counts) > 0, "Should detect some events"
    
    print(f"  ✓ Analyzer initialized with {analyzer.total_days} days of data")


def test_multiple_event_probabilities():
    """Test calculation of multiple event probabilities."""
    print("Testing multiple event probabilities...")
    
    data = generate_sample_data(years=10)
    analyzer = ClimateEventAnalyzer(data)
    
    probabilities = analyzer.calculate_all_probabilities(365)
    
    assert isinstance(probabilities, dict), "Should return a dictionary"
    assert len(probabilities) > 0, "Should calculate some probabilities"
    
    for event, prob in probabilities.items():
        assert 0 <= prob <= 1, f"Probability for {event} should be between 0 and 1"
    
    print(f"  ✓ Calculated {len(probabilities)} event probabilities")


def test_seasonal_probability():
    """Test seasonal probability calculation."""
    print("Testing seasonal probability...")
    
    data = generate_sample_data(years=10)
    analyzer = ClimateEventAnalyzer(data)
    
    # Test all seasons
    seasons = ['northeast_monsoon', 'southwest_monsoon', 'inter_monsoon']
    for season in seasons:
        prob = analyzer.get_seasonal_probability('flood', season)
        assert 0 <= prob <= 1, f"Probability for {season} should be between 0 and 1"
    
    print("  ✓ Seasonal probabilities calculated successfully")


def test_trend_prediction():
    """Test trend prediction."""
    print("Testing trend prediction...")
    
    data = generate_sample_data(years=15)
    analyzer = ClimateEventAnalyzer(data)
    
    trend_info = analyzer.predict_trend('flood', years_ahead=5)
    
    assert 'trend' in trend_info, "Should return trend"
    assert 'current_probability' in trend_info, "Should return current probability"
    assert 'predicted_probability' in trend_info, "Should return predicted probability"
    assert 'confidence' in trend_info, "Should return confidence level"
    
    assert trend_info['trend'] in ['increasing', 'decreasing', 'stable', 'insufficient_data']
    assert trend_info['confidence'] in ['high', 'medium', 'low']
    
    print(f"  ✓ Trend prediction: {trend_info['trend']} (confidence: {trend_info['confidence']})")


def test_different_time_windows():
    """Test probability calculation with different time windows."""
    print("Testing different time windows...")
    
    data = generate_sample_data(years=10)
    analyzer = ClimateEventAnalyzer(data)
    
    windows = [30, 90, 180, 365]
    previous_prob = 0
    
    for window in windows:
        prob = analyzer.calculate_event_probability('flood', window)
        # Longer time windows should generally have higher or equal probability
        assert prob >= previous_prob or abs(prob - previous_prob) < 0.01, \
            f"Probability should increase or stay similar with longer windows"
        previous_prob = prob
    
    print("  ✓ Time window calculations work correctly")


def test_custom_data():
    """Test with custom data."""
    print("Testing with custom data...")
    
    # Create custom data with known events
    dates = pd.date_range('2020-01-01', periods=1000)
    rainfall = np.random.gamma(2, 20, 1000)
    
    # Add exactly 10 flood events
    flood_indices = [100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
    for idx in flood_indices:
        rainfall[idx] = 180  # Above flood threshold
    
    custom_data = pd.DataFrame({
        'date': dates,
        'rainfall': rainfall
    })
    
    analyzer = ClimateEventAnalyzer(custom_data)
    
    assert analyzer.event_counts['flood'] >= 10, "Should detect at least 10 flood events"
    
    print(f"  ✓ Custom data processed: {analyzer.event_counts['flood']} floods detected")


def test_regional_data():
    """Test different regional data."""
    print("Testing regional data...")
    
    regions = ['peninsular', 'sabah', 'sarawak']
    
    for region in regions:
        data = generate_sample_data(years=5, location=region)
        analyzer = ClimateEventAnalyzer(data)
        prob = analyzer.calculate_event_probability('heavy_rainfall', 365)
        
        assert 0 <= prob <= 1, f"Probability for {region} should be valid"
    
    print("  ✓ All regional data processed successfully")


def test_empty_data_handling():
    """Test handling of edge cases."""
    print("Testing edge cases...")
    
    # Test with empty DataFrame
    empty_data = pd.DataFrame()
    analyzer = ClimateEventAnalyzer(empty_data)
    prob = analyzer.calculate_event_probability('flood', 365)
    
    assert prob == 0.0, "Empty data should return 0 probability"
    
    # Test with minimal data
    minimal_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'rainfall': [10] * 10,
        'temperature': [27] * 10
    })
    
    analyzer = ClimateEventAnalyzer(minimal_data)
    prob = analyzer.calculate_event_probability('flood', 365)
    
    assert 0 <= prob <= 1, "Minimal data should return valid probability"
    
    print("  ✓ Edge cases handled correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("Running Climate Probability Module Tests")
    print("="*70 + "\n")
    
    tests = [
        test_generate_sample_data,
        test_basic_probability_calculation,
        test_analyzer_initialization,
        test_multiple_event_probabilities,
        test_seasonal_probability,
        test_trend_prediction,
        test_different_time_windows,
        test_custom_data,
        test_regional_data,
        test_empty_data_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Test error: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
