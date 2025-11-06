"""
Validadores para datos de entrada de la librería de daños por inundación.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict, Any
from .exceptions import DataValidationError

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valida coordenadas geográficas.
    
    Args:
        latitude: Latitud en grados decimales
        longitude: Longitud en grados decimales
        
    Returns:
        bool: True si las coordenadas son válidas
        
    Raises:
        DataValidationError: Si las coordenadas no son válidas
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise DataValidationError("Las coordenadas deben ser números")
    
    if not (-90 <= latitude <= 90):
        raise DataValidationError(f"Latitud {latitude} fuera del rango válido [-90, 90]")
    
    if not (-180 <= longitude <= 180):
        raise DataValidationError(f"Longitud {longitude} fuera del rango válido [-180, 180]")
    
    return True

def validate_flood_depth(depth: float) -> bool:
    """
    Valida la profundidad de inundación.
    
    Args:
        depth: Profundidad de inundación en metros
        
    Returns:
        bool: True si la profundidad es válida
        
    Raises:
        DataValidationError: Si la profundidad no es válida
    """
    if not isinstance(depth, (int, float)):
        raise DataValidationError("La profundidad debe ser un número")
    
    if depth < 0:
        raise DataValidationError("La profundidad no puede ser negativa")
    
    if depth > 20:  # Límite razonable para inundaciones
        raise DataValidationError(f"Profundidad {depth}m parece excesiva (>20m)")
    
    return True

def validate_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida todos los datos de entrada para el cálculo de daños.
    
    Args:
        data: Diccionario con los datos de entrada
        
    Returns:
        Dict: Datos validados y normalizados
        
    Raises:
        DataValidationError: Si algún dato no es válido
    """
    required_fields = ['latitude', 'longitude', 'flood_depth']
    
    # Verificar campos requeridos
    for field in required_fields:
        if field not in data:
            raise DataValidationError(f"Campo requerido '{field}' no encontrado")
    
    # Validar coordenadas
    validate_coordinates(data['latitude'], data['longitude'])
    
    # Validar profundidad
    validate_flood_depth(data['flood_depth'])
    
    # Validar campos opcionales si están presentes
    if 'land_use_type' in data:
        if not isinstance(data['land_use_type'], str):
            raise DataValidationError("El tipo de uso de suelo debe ser texto")
    
    if 'building_type' in data:
        if not isinstance(data['building_type'], str):
            raise DataValidationError("El tipo de edificación debe ser texto")
    
    if 'area' in data:
        if not isinstance(data['area'], (int, float)) or data['area'] <= 0:
            raise DataValidationError("El área debe ser un número positivo")
    
    return data

def validate_parquet_schema(df: pd.DataFrame, expected_columns: list) -> bool:
    """
    Valida que un DataFrame tenga las columnas esperadas.
    
    Args:
        df: DataFrame a validar
        expected_columns: Lista de columnas esperadas
        
    Returns:
        bool: True si el esquema es válido
        
    Raises:
        DataValidationError: Si faltan columnas requeridas
    """
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise DataValidationError(f"Columnas faltantes: {missing_columns}")
    
    return True