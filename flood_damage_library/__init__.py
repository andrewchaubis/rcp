"""
Flood Damage Calculation Library.

This library provides tools for calculating economic damages
caused by floods based on:
- Geographic location
- Flood depth
- Affected area characteristics
- Specific damage functions by land use type

Includes support for:
- JRC (Joint Research Centre) data with global functions
- Damage functions by region (Europe, America, Asia, etc.)
- Maximum damage values by country
- Uncertainty analysis
"""

__version__ = "2.0.0"
__author__ = "Flood Damage Analysis Team"

from .core.damage_calculator import FloodDamageCalculator
from .core.jrc_damage_calculator import JRCFloodDamageCalculator
from .core.data_manager import DataManager
from .utils.validators import validate_input_data
from .utils.exceptions import FloodDamageError, DataValidationError

__all__ = [
    'FloodDamageCalculator',
    'JRCFloodDamageCalculator',
    'DataManager', 
    'validate_input_data',
    'FloodDamageError',
    'DataValidationError'
]