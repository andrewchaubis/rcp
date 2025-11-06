"""
Excepciones personalizadas para la librería de daños por inundación.
"""

class FloodDamageError(Exception):
    """Excepción base para errores de la librería de daños por inundación."""
    pass

class DataValidationError(FloodDamageError):
    """Excepción para errores de validación de datos de entrada."""
    pass

class DataNotFoundError(FloodDamageError):
    """Excepción cuando no se encuentran datos necesarios."""
    pass

class CalculationError(FloodDamageError):
    """Excepción para errores en los cálculos de daño."""
    pass

class LocationError(FloodDamageError):
    """Excepción para errores relacionados con ubicación geográfica."""
    pass