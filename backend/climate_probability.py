"""
Climate Event Probability Analysis for Malaysia

This module provides functions to analyze historical climate data and determine
the probability of major climate events in Malaysia, including floods, droughts,
heatwaves, and heavy rainfall.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
from scipy import stats
from collections import defaultdict


class ClimateEventAnalyzer:
    """Analyzes historical climate data to determine event probabilities."""
    
    # Climate event thresholds for Malaysia (floods and rainfall only)
    THRESHOLDS = {
        'heavy_rainfall': 100,  # mm per day
        'extreme_rainfall': 200,  # mm per day
        'flood_rainfall': 150,  # mm in 24 hours
    }
    
    def __init__(self, historical_data: Optional[pd.DataFrame] = None):
        """
        Initialize the analyzer with historical climate data.
        
        Args:
            historical_data: DataFrame with columns ['date', 'rainfall', 'event_type']
                           Note: Only rainfall data is used for analysis
        """
        self.historical_data = historical_data
        self.event_counts = defaultdict(int)
        self.total_days = 0
        
        if historical_data is not None:
            self._process_historical_data()
    
    def _process_historical_data(self):
        """Process historical data to count climate events (floods and rainfall only)."""
        if self.historical_data is None or len(self.historical_data) == 0:
            return
        
        self.total_days = len(self.historical_data)
        
        # Count different types of rainfall events
        if 'rainfall' in self.historical_data.columns:
            self.event_counts['heavy_rainfall'] = (
                self.historical_data['rainfall'] >= self.THRESHOLDS['heavy_rainfall']
            ).sum()
            self.event_counts['extreme_rainfall'] = (
                self.historical_data['rainfall'] >= self.THRESHOLDS['extreme_rainfall']
            ).sum()
            self.event_counts['flood'] = (
                self.historical_data['rainfall'] >= self.THRESHOLDS['flood_rainfall']
            ).sum()
        
        # If event_type column exists, use it directly (only for flood/rainfall events)
        if 'event_type' in self.historical_data.columns:
            event_type_counts = self.historical_data['event_type'].value_counts()
            for event, count in event_type_counts.items():
                if event and str(event).lower() != 'none':
                    event_lower = str(event).lower()
                    # Only count flood and rainfall related events
                    if 'flood' in event_lower or 'rainfall' in event_lower or 'rain' in event_lower:
                        self.event_counts[event_lower] += count
    

    
    def calculate_event_probability(
        self, 
        event_type: str, 
        time_window: int = 365
    ) -> float:
        """
        Calculate the probability of a specific climate event.
        
        Args:
            event_type: Type of climate event ('flood', 'heavy_rainfall', 'extreme_rainfall')
            time_window: Number of days to consider for probability (default: 365)
        
        Returns:
            Probability of the event occurring within the time window (0-1)
        """
        if self.total_days == 0:
            return 0.0
        
        event_count = self.event_counts.get(event_type.lower(), 0)
        
        # Calculate daily probability
        daily_probability = event_count / self.total_days
        
        # Calculate probability for the time window
        # Using complement probability: P(at least one event) = 1 - P(no events)
        probability_no_events = (1 - daily_probability) ** time_window
        probability_at_least_one = 1 - probability_no_events
        
        return min(probability_at_least_one, 1.0)
    
    def calculate_all_probabilities(
        self, 
        time_window: int = 365
    ) -> Dict[str, float]:
        """
        Calculate probabilities for all tracked climate events.
        
        Args:
            time_window: Number of days to consider for probability (default: 365)
        
        Returns:
            Dictionary mapping event types to their probabilities
        """
        probabilities = {}
        for event_type in self.event_counts.keys():
            probabilities[event_type] = self.calculate_event_probability(
                event_type, time_window
            )
        return probabilities
    
    def get_seasonal_probability(
        self, 
        event_type: str, 
        season: str
    ) -> float:
        """
        Calculate probability of an event during a specific season.
        
        Args:
            event_type: Type of climate event
            season: Season name ('northeast_monsoon', 'southwest_monsoon', 'inter_monsoon')
        
        Returns:
            Probability of the event during that season
        """
        if self.historical_data is None or 'date' not in self.historical_data.columns:
            return 0.0
        
        # Define seasons for Malaysia
        season_months = {
            'northeast_monsoon': [11, 12, 1, 2, 3],  # Nov - Mar (wet season)
            'southwest_monsoon': [5, 6, 7, 8, 9],    # May - Sep (dry season)
            'inter_monsoon': [4, 10],                # Apr, Oct (transition)
        }
        
        if season not in season_months:
            raise ValueError(f"Unknown season: {season}")
        
        # Filter data for the specified season
        df = self.historical_data.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        df['month'] = df['date'].dt.month
        season_data = df[df['month'].isin(season_months[season])]
        
        if len(season_data) == 0:
            return 0.0
        
        # Count rainfall/flood events in this season
        event_count = 0
        if 'rainfall' in season_data.columns:
            if event_type == 'heavy_rainfall':
                event_count = (season_data['rainfall'] >= self.THRESHOLDS['heavy_rainfall']).sum()
            elif event_type == 'extreme_rainfall':
                event_count = (season_data['rainfall'] >= self.THRESHOLDS['extreme_rainfall']).sum()
            elif event_type == 'flood':
                event_count = (season_data['rainfall'] >= self.THRESHOLDS['flood_rainfall']).sum()
        
        return event_count / len(season_data) if len(season_data) > 0 else 0.0
    
    def predict_trend(
        self, 
        event_type: str, 
        years_ahead: int = 5
    ) -> Dict[str, Union[float, str]]:
        """
        Predict the trend of climate events for future years.
        
        Args:
            event_type: Type of climate event
            years_ahead: Number of years to predict ahead
        
        Returns:
            Dictionary with trend information and predicted probability
        """
        if self.historical_data is None or len(self.historical_data) == 0:
            return {
                'trend': 'insufficient_data',
                'current_probability': 0.0,
                'predicted_probability': 0.0,
                'confidence': 'low'
            }
        
        # Calculate yearly event counts
        df = self.historical_data.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        df['year'] = df['date'].dt.year
        yearly_stats = []
        
        for year in sorted(df['year'].unique()):
            year_data = df[df['year'] == year]
            year_events = 0
            
            if 'rainfall' in year_data.columns:
                if event_type == 'heavy_rainfall':
                    year_events = (year_data['rainfall'] >= self.THRESHOLDS['heavy_rainfall']).sum()
                elif event_type == 'extreme_rainfall':
                    year_events = (year_data['rainfall'] >= self.THRESHOLDS['extreme_rainfall']).sum()
                elif event_type == 'flood':
                    year_events = (year_data['rainfall'] >= self.THRESHOLDS['flood_rainfall']).sum()
            
            yearly_stats.append((year, year_events))
        
        if len(yearly_stats) < 2:
            return {
                'trend': 'insufficient_data',
                'current_probability': self.calculate_event_probability(event_type),
                'predicted_probability': self.calculate_event_probability(event_type),
                'confidence': 'low'
            }
        
        # Linear regression for trend analysis
        years = np.array([y[0] for y in yearly_stats])
        events = np.array([y[1] for y in yearly_stats])
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, events)
        
        # Predict future events
        future_year = years[-1] + years_ahead
        predicted_events = slope * future_year + intercept
        predicted_events = max(0, predicted_events)  # Can't be negative
        
        # Determine trend
        if slope > 0.5:
            trend = 'increasing'
        elif slope < -0.5:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Confidence based on R-squared
        confidence = 'high' if r_value ** 2 > 0.7 else 'medium' if r_value ** 2 > 0.4 else 'low'
        
        current_prob = self.calculate_event_probability(event_type)
        
        # Estimate future probability (rough approximation)
        if slope != 0:
            avg_events_per_year = np.mean(events)
            multiplier = predicted_events / avg_events_per_year if avg_events_per_year > 0 else 1
            predicted_prob = min(current_prob * multiplier, 1.0)
        else:
            predicted_prob = current_prob
        
        return {
            'trend': trend,
            'slope': float(slope),
            'current_probability': float(current_prob),
            'predicted_probability': float(predicted_prob),
            'confidence': confidence,
            'r_squared': float(r_value ** 2)
        }


def calculate_climate_event_probability(
    historical_data: pd.DataFrame,
    event_type: str,
    time_window: int = 365
) -> float:
    """
    Main function to calculate probability of a major climate event in Malaysia.
    
    Args:
        historical_data: DataFrame containing historical climate data with columns:
                        - 'date': Date of observation
                        - 'rainfall': Daily rainfall in mm (required)
                        - 'event_type': Type of event that occurred (optional)
        event_type: Type of climate event to analyze. Options:
                   - 'flood': Flooding events
                   - 'heavy_rainfall': Heavy rainfall days
                   - 'extreme_rainfall': Extreme rainfall events
        time_window: Number of days to calculate probability for (default: 365 days)
    
    Returns:
        Probability (0-1) of the event occurring within the specified time window
    
    Example:
        >>> data = pd.DataFrame({
        ...     'date': pd.date_range('2020-01-01', periods=1000),
        ...     'rainfall': np.random.gamma(2, 20, 1000)
        ... })
        >>> prob = calculate_climate_event_probability(data, 'flood', 365)
        >>> print(f"Flood probability: {prob:.2%}")
    """
    analyzer = ClimateEventAnalyzer(historical_data)
    return analyzer.calculate_event_probability(event_type, time_window)


def generate_sample_data(
    years: int = 10,
    location: str = 'peninsular'
) -> pd.DataFrame:
    """
    Generate sample climate data for Malaysia for testing purposes.
    
    Args:
        years: Number of years of data to generate
        location: Region of Malaysia ('peninsular', 'sabah', 'sarawak')
    
    Returns:
        DataFrame with synthetic climate data (rainfall only)
    """
    days = years * 365
    dates = pd.date_range(end=datetime.now(), periods=days)
    
    # Regional rainfall characteristics
    climate_params = {
        'peninsular': {'rain_alpha': 2, 'rain_beta': 25},
        'sabah': {'rain_alpha': 2.5, 'rain_beta': 30},
        'sarawak': {'rain_alpha': 2.3, 'rain_beta': 28},
    }
    
    params = climate_params.get(location, climate_params['peninsular'])
    
    # Generate synthetic data with seasonal patterns
    months = np.array([d.month for d in dates])
    
    # Rainfall with monsoon patterns (higher in Nov-Mar for NE monsoon)
    monsoon_factor = np.where(
        (months >= 11) | (months <= 3),
        1.5,  # NE monsoon season
        np.where(
            (months >= 5) & (months <= 9),
            0.7,  # SW monsoon (drier)
            1.0   # Inter-monsoon
        )
    )
    rainfall = np.random.gamma(params['rain_alpha'], params['rain_beta'], days) * monsoon_factor
    
    # Add some extreme events
    extreme_indices = np.random.choice(days, size=int(days * 0.02), replace=False)
    rainfall[extreme_indices] *= np.random.uniform(3, 8, len(extreme_indices))
    
    df = pd.DataFrame({
        'date': dates,
        'rainfall': rainfall,
    })
    
    # Classify rainfall/flood events
    events = []
    for _, row in df.iterrows():
        if row['rainfall'] >= 200:
            events.append('extreme_rainfall')
        elif row['rainfall'] >= 150:
            events.append('flood')
        elif row['rainfall'] >= 100:
            events.append('heavy_rainfall')
        else:
            events.append(None)
    
    df['event_type'] = events
    
    return df


if __name__ == '__main__':
    # Example usage
    print("Climate Event Probability Analysis for Malaysia")
    print("(Floods and Rainfall Events)")
    print("=" * 60)
    
    # Generate sample data
    print("\n1. Generating sample rainfall data (10 years)...")
    data = generate_sample_data(years=10, location='peninsular')
    print(f"   Generated {len(data)} days of data")
    print(f"   Date range: {data['date'].min()} to {data['date'].max()}")
    
    # Initialize analyzer
    print("\n2. Analyzing historical rainfall data...")
    analyzer = ClimateEventAnalyzer(data)
    
    # Calculate probabilities
    print("\n3. Rainfall & Flood Event Probabilities (1-year window):")
    print("-" * 60)
    probabilities = analyzer.calculate_all_probabilities(time_window=365)
    for event, prob in sorted(probabilities.items()):
        print(f"   {event.replace('_', ' ').title()}: {prob:.2%}")
    
    # Seasonal analysis
    print("\n4. Seasonal Analysis (Flood Risk):")
    print("-" * 60)
    seasons = ['northeast_monsoon', 'southwest_monsoon', 'inter_monsoon']
    for season in seasons:
        prob = analyzer.get_seasonal_probability('flood', season)
        print(f"   {season.replace('_', ' ').title()}: {prob:.2%}")
    
    # Trend prediction
    print("\n5. 5-Year Trend Prediction (Flood Events):")
    print("-" * 60)
    trend_info = analyzer.predict_trend('flood', years_ahead=5)
    print(f"   Trend: {trend_info['trend'].upper()}")
    print(f"   Current Probability: {trend_info['current_probability']:.2%}")
    print(f"   Predicted Probability (5 years): {trend_info['predicted_probability']:.2%}")
    print(f"   Confidence: {trend_info['confidence'].upper()}")
    print(f"   R-squared: {trend_info['r_squared']:.3f}")
    
    # Example with simple function call
    print("\n6. Simple Function Usage:")
    print("-" * 60)
    flood_prob = calculate_climate_event_probability(data, 'flood', 365)
    print(f"   Flood probability (next year): {flood_prob:.2%}")
    print(f"\n   Note: Analysis focuses on rainfall-based events only")
