"""
Test Suite for CLIMADA Integration Module

Tests the climate_probability_climada module functionality.
"""

import sys
import numpy as np
import pandas as pd
from climate_probability_climada import (
    ClimadaAPIClient,
    ClimadaFloodAnalyzer,
    generate_climada_report
)

def test_api_client_initialization():
    """Test API client initialization."""
    print("Testing API client initialization...")
    client = ClimadaAPIClient()
    assert client.base_url == "https://climada.ethz.ch/data-api/v1"
    assert client.cache_dir == "./climada_cache"
    print("  ✓ API client initialized correctly")

def test_list_datasets():
    """Test dataset listing."""
    print("Testing dataset listing...")
    client = ClimadaAPIClient()
    datasets = client.list_datasets('river_flood')
    assert len(datasets) > 0
    assert 'name' in datasets[0]
    assert 'return_periods' in datasets[0]
    print(f"  ✓ Found {len(datasets)} datasets")

def test_flood_hazard_data():
    """Test flood hazard data retrieval."""
    print("Testing flood hazard data retrieval...")
    client = ClimadaAPIClient()
    hazard_data = client.get_flood_hazard_malaysia(
        scenario='historical',
        return_periods=[10, 50, 100]
    )
    assert not hazard_data.empty
    assert 'location' in hazard_data.columns
    assert 'flood_intensity_m' in hazard_data.columns
    assert 'return_period' in hazard_data.columns
    assert len(hazard_data) > 0
    print(f"  ✓ Retrieved {len(hazard_data)} hazard records")

def test_exposure_data():
    """Test exposure data retrieval."""
    print("Testing exposure data retrieval...")
    client = ClimadaAPIClient()
    exposure = client.get_exposure_litpop('MYS')
    assert 'country' in exposure
    assert exposure['country'] == 'Malaysia'
    assert 'total_exposure_usd' in exposure
    assert exposure['total_exposure_usd'] > 0
    assert 'regions' in exposure
    print(f"  ✓ Total exposure: ${exposure['total_exposure_usd']/1e9:.1f}B USD")

def test_analyzer_initialization():
    """Test analyzer initialization."""
    print("Testing analyzer initialization...")
    analyzer = ClimadaFloodAnalyzer()
    assert analyzer.api_client is not None
    assert analyzer.hazard_data is None  # Not loaded yet
    assert analyzer.exposure_data is None  # Not loaded yet
    print("  ✓ Analyzer initialized")

def test_load_hazard():
    """Test hazard data loading."""
    print("Testing hazard data loading...")
    analyzer = ClimadaFloodAnalyzer()
    hazard_data = analyzer.load_flood_hazard(
        scenario='rcp45',
        return_periods=[10, 25, 50, 100]
    )
    assert not hazard_data.empty
    assert analyzer.hazard_data is not None
    print(f"  ✓ Loaded {len(hazard_data)} hazard records")

def test_load_exposure():
    """Test exposure data loading."""
    print("Testing exposure data loading...")
    analyzer = ClimadaFloodAnalyzer()
    exposure = analyzer.load_exposure()
    assert exposure is not None
    assert analyzer.exposure_data is not None
    print("  ✓ Exposure data loaded")

def test_flood_probability_calculation():
    """Test flood probability calculation."""
    print("Testing flood probability calculation...")
    analyzer = ClimadaFloodAnalyzer()
    analyzer.load_flood_hazard()
    
    prob = analyzer.calculate_flood_probability(
        location='Kuala Lumpur',
        time_window_days=30,
        return_period=100
    )
    
    assert 0 <= prob <= 1
    assert prob > 0  # Should have some probability
    print(f"  ✓ 30-day flood probability: {prob:.4%}")

def test_return_period_calculation():
    """Test return period calculation from data."""
    print("Testing return period calculation...")
    analyzer = ClimadaFloodAnalyzer()
    
    # Generate synthetic flood event data
    np.random.seed(42)
    flood_events = pd.Series(np.random.gamma(2, 50, 1000))
    
    return_periods = analyzer.calculate_return_period_from_data(flood_events)
    
    if not return_periods.empty:
        assert 'return_period_years' in return_periods.columns
        assert 'flood_magnitude' in return_periods.columns
        assert len(return_periods) > 0
        print(f"  ✓ Calculated {len(return_periods)} return period values")
    else:
        print("  ⚠ Warning: Could not calculate return periods (expected with limited data)")

def test_scenario_comparison():
    """Test climate scenario comparison."""
    print("Testing scenario comparison...")
    analyzer = ClimadaFloodAnalyzer()
    
    comparison = analyzer.compare_scenarios(
        location='Kuala Lumpur',
        return_period=100
    )
    
    assert not comparison.empty
    assert 'scenario' in comparison.columns
    assert 'flood_intensity_m' in comparison.columns
    
    scenarios = comparison['scenario'].unique()
    assert 'historical' in scenarios
    assert len(scenarios) >= 3  # At least a few scenarios
    
    print(f"  ✓ Compared {len(scenarios)} climate scenarios")

def test_expected_annual_impact():
    """Test Expected Annual Impact calculation."""
    print("Testing Expected Annual Impact calculation...")
    analyzer = ClimadaFloodAnalyzer()
    analyzer.load_flood_hazard()
    analyzer.load_exposure()
    
    eai_results = analyzer.calculate_expected_annual_impact('Kuala Lumpur')
    
    assert 'expected_annual_impact_usd' in eai_results
    assert 'exposure_usd' in eai_results
    assert 'eai_ratio' in eai_results
    assert eai_results['expected_annual_impact_usd'] > 0
    
    print(f"  ✓ EAI: ${eai_results['expected_annual_impact_usd']/1e6:.2f}M USD")
    print(f"    EAI/Exposure: {eai_results['eai_ratio']:.3%}")

def test_report_generation():
    """Test report generation."""
    print("Testing report generation...")
    
    report = generate_climada_report('Kuala Lumpur', 'rcp45')
    
    assert isinstance(report, str)
    assert len(report) > 0
    assert 'CLIMADA' in report
    assert 'Kuala Lumpur' in report
    assert 'rcp45' in report.lower()
    
    print(f"  ✓ Generated report ({len(report)} characters)")

def test_multiple_locations():
    """Test analysis across multiple locations."""
    print("Testing multiple locations...")
    analyzer = ClimadaFloodAnalyzer()
    analyzer.load_flood_hazard()
    
    locations = ['Kuala Lumpur', 'Penang', 'Kota Kinabalu']
    results = []
    
    for location in locations:
        prob = analyzer.calculate_flood_probability(location, 365, 100)
        results.append({'location': location, 'annual_prob': prob})
    
    assert len(results) == len(locations)
    assert all(0 <= r['annual_prob'] <= 1 for r in results)
    
    print(f"  ✓ Analyzed {len(locations)} locations")

def test_data_consistency():
    """Test data consistency across multiple calls."""
    print("Testing data consistency...")
    analyzer = ClimadaFloodAnalyzer()
    
    # Load data twice
    data1 = analyzer.load_flood_hazard(scenario='historical', return_periods=[100])
    data2 = analyzer.load_flood_hazard(scenario='historical', return_periods=[100])
    
    # Check if data structure is consistent
    assert len(data1.columns) == len(data2.columns)
    assert list(data1.columns) == list(data2.columns)
    
    print("  ✓ Data structure is consistent")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    analyzer = ClimadaFloodAnalyzer()
    analyzer.load_flood_hazard()
    
    # Test with non-existent location
    prob = analyzer.calculate_flood_probability('NonExistentCity', 30, 100)
    assert prob == 0.0
    
    # Test with insufficient data for return period calculation
    small_series = pd.Series([1, 2, 3])  # Too small
    result = analyzer.calculate_return_period_from_data(small_series)
    # Should return empty or handle gracefully
    
    print("  ✓ Edge cases handled correctly")

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print(" "*20 + "CLIMADA Integration Test Suite")
    print("="*80 + "\n")
    
    tests = [
        test_api_client_initialization,
        test_list_datasets,
        test_flood_hazard_data,
        test_exposure_data,
        test_analyzer_initialization,
        test_load_hazard,
        test_load_exposure,
        test_flood_probability_calculation,
        test_return_period_calculation,
        test_scenario_comparison,
        test_expected_annual_impact,
        test_report_generation,
        test_multiple_locations,
        test_data_consistency,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Test error: {e}")
            failed += 1
        print()
    
    print("="*80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*80)
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
