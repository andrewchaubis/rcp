"""
Gestor de datos para la librería de daños por inundación.
Maneja la carga y procesamiento de archivos parquet y otros datos de referencia.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from ..utils.exceptions import DataNotFoundError, DataValidationError
from ..utils.validators import validate_parquet_schema

class DataManager:
    """
    Gestor de datos para cargar y manejar información de referencia
    necesaria para los cálculos de daño por inundación.
    """
    
    def __init__(self, data_directory: Optional[str] = None):
        """
        Inicializa el gestor de datos.
        
        Args:
            data_directory: Directorio donde se encuentran los archivos de datos
        """
        self.data_directory = Path(data_directory) if data_directory else Path("./data")
        self.loaded_data = {}
        self._damage_functions = None
        self._land_use_data = None
        self._building_types = None
        
    def load_parquet_file(self, filename: str, expected_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Carga un archivo parquet y valida su esquema.
        
        Args:
            filename: Nombre del archivo parquet
            expected_columns: Lista de columnas esperadas (opcional)
            
        Returns:
            pd.DataFrame: Datos cargados
            
        Raises:
            DataNotFoundError: Si el archivo no existe
            DataValidationError: Si el esquema no es válido
        """
        file_path = self.data_directory / filename
        
        if not file_path.exists():
            raise DataNotFoundError(f"Archivo no encontrado: {file_path}")
        
        try:
            df = pd.read_parquet(file_path)
            
            if expected_columns:
                validate_parquet_schema(df, expected_columns)
            
            self.loaded_data[filename] = df
            return df
            
        except Exception as e:
            raise DataValidationError(f"Error al cargar {filename}: {str(e)}")
    
    def load_damage_functions(self, filename: str = "damage_functions.parquet") -> pd.DataFrame:
        """
        Carga las funciones de daño desde un archivo parquet.
        
        Args:
            filename: Nombre del archivo con funciones de daño
            
        Returns:
            pd.DataFrame: Funciones de daño cargadas
        """
        expected_columns = ['land_use_type', 'building_type', 'depth', 'damage_ratio']
        self._damage_functions = self.load_parquet_file(filename, expected_columns)
        return self._damage_functions
    
    def load_land_use_data(self, filename: str = "land_use.parquet") -> pd.DataFrame:
        """
        Carga datos de uso de suelo desde un archivo parquet.
        
        Args:
            filename: Nombre del archivo con datos de uso de suelo
            
        Returns:
            pd.DataFrame: Datos de uso de suelo cargados
        """
        expected_columns = ['latitude', 'longitude', 'land_use_type']
        self._land_use_data = self.load_parquet_file(filename, expected_columns)
        return self._land_use_data
    
    def load_building_types(self, filename: str = "building_types.parquet") -> pd.DataFrame:
        """
        Carga datos de tipos de edificación desde un archivo parquet.
        
        Args:
            filename: Nombre del archivo con tipos de edificación
            
        Returns:
            pd.DataFrame: Datos de tipos de edificación cargados
        """
        expected_columns = ['latitude', 'longitude', 'building_type', 'value_per_m2']
        self._building_types = self.load_parquet_file(filename, expected_columns)
        return self._building_types
    
    def get_land_use_at_location(self, latitude: float, longitude: float, 
                                tolerance: float = 0.001) -> Optional[str]:
        """
        Obtiene el tipo de uso de suelo en una ubicación específica.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            tolerance: Tolerancia para la búsqueda de ubicación
            
        Returns:
            str: Tipo de uso de suelo o None si no se encuentra
        """
        if self._land_use_data is None:
            self.load_land_use_data()
        
        # Buscar la ubicación más cercana dentro de la tolerancia
        mask = (
            (abs(self._land_use_data['latitude'] - latitude) <= tolerance) &
            (abs(self._land_use_data['longitude'] - longitude) <= tolerance)
        )
        
        matches = self._land_use_data[mask]
        
        if len(matches) > 0:
            # Si hay múltiples coincidencias, tomar la más cercana
            distances = np.sqrt(
                (matches['latitude'] - latitude)**2 + 
                (matches['longitude'] - longitude)**2
            )
            closest_idx = distances.idxmin()
            return matches.loc[closest_idx, 'land_use_type']
        
        return None
    
    def get_building_type_at_location(self, latitude: float, longitude: float,
                                    tolerance: float = 0.001) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de edificación en una ubicación específica.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            tolerance: Tolerancia para la búsqueda de ubicación
            
        Returns:
            Dict: Información de edificación o None si no se encuentra
        """
        if self._building_types is None:
            self.load_building_types()
        
        # Buscar la ubicación más cercana dentro de la tolerancia
        mask = (
            (abs(self._building_types['latitude'] - latitude) <= tolerance) &
            (abs(self._building_types['longitude'] - longitude) <= tolerance)
        )
        
        matches = self._building_types[mask]
        
        if len(matches) > 0:
            # Si hay múltiples coincidencias, tomar la más cercana
            distances = np.sqrt(
                (matches['latitude'] - latitude)**2 + 
                (matches['longitude'] - longitude)**2
            )
            closest_idx = distances.idxmin()
            result = matches.loc[closest_idx]
            
            return {
                'building_type': result['building_type'],
                'value_per_m2': result['value_per_m2']
            }
        
        return None
    
    def get_damage_function(self, land_use_type: str, building_type: str) -> Optional[pd.DataFrame]:
        """
        Obtiene la función de daño para un tipo específico de uso de suelo y edificación.
        
        Args:
            land_use_type: Tipo de uso de suelo
            building_type: Tipo de edificación
            
        Returns:
            pd.DataFrame: Función de daño (profundidad vs ratio de daño)
        """
        if self._damage_functions is None:
            self.load_damage_functions()
        
        mask = (
            (self._damage_functions['land_use_type'] == land_use_type) &
            (self._damage_functions['building_type'] == building_type)
        )
        
        damage_func = self._damage_functions[mask]
        
        if len(damage_func) > 0:
            return damage_func[['depth', 'damage_ratio']].sort_values('depth')
        
        return None
    
    def list_available_data(self) -> Dict[str, Any]:
        """
        Lista todos los datos disponibles cargados.
        
        Returns:
            Dict: Información sobre los datos cargados
        """
        info = {
            'loaded_files': list(self.loaded_data.keys()),
            'damage_functions_loaded': self._damage_functions is not None,
            'land_use_data_loaded': self._land_use_data is not None,
            'building_types_loaded': self._building_types is not None
        }
        
        if self._damage_functions is not None:
            info['damage_functions_shape'] = self._damage_functions.shape
            info['available_land_uses'] = self._damage_functions['land_use_type'].unique().tolist()
            info['available_building_types'] = self._damage_functions['building_type'].unique().tolist()
        
        return info