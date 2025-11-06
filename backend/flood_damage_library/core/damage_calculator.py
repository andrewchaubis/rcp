"""
Calculadora principal de daños por inundación.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from scipy.interpolate import interp1d
from .data_manager import DataManager
from ..utils.validators import validate_input_data
from ..utils.exceptions import CalculationError, DataNotFoundError

class FloodDamageCalculator:
    """
    Calculadora principal para estimar daños económicos por inundaciones.
    """
    
    def __init__(self, data_directory: Optional[str] = None):
        """
        Inicializa la calculadora de daños.
        
        Args:
            data_directory: Directorio con los archivos de datos de referencia
        """
        self.data_manager = DataManager(data_directory)
        self._default_values = {
            'residential_value_per_m2': 1000,  # USD por m²
            'commercial_value_per_m2': 1500,   # USD por m²
            'industrial_value_per_m2': 800,    # USD por m²
            'default_area': 100,               # m²
        }
    
    def calculate_damage(self, 
                        latitude: float,
                        longitude: float, 
                        flood_depth: float,
                        land_use_type: Optional[str] = None,
                        building_type: Optional[str] = None,
                        area: Optional[float] = None,
                        value_per_m2: Optional[float] = None) -> Dict[str, Any]:
        """
        Calcula el daño económico por inundación en una ubicación específica.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            flood_depth: Profundidad de inundación en metros
            land_use_type: Tipo de uso de suelo (opcional, se infiere si no se proporciona)
            building_type: Tipo de edificación (opcional, se infiere si no se proporciona)
            area: Área afectada en m² (opcional, usa valor por defecto)
            value_per_m2: Valor por m² (opcional, se infiere si no se proporciona)
            
        Returns:
            Dict: Resultados del cálculo de daño
            
        Raises:
            CalculationError: Si no se puede realizar el cálculo
        """
        # Validar datos de entrada
        input_data = {
            'latitude': latitude,
            'longitude': longitude,
            'flood_depth': flood_depth
        }
        
        if land_use_type:
            input_data['land_use_type'] = land_use_type
        if building_type:
            input_data['building_type'] = building_type
        if area:
            input_data['area'] = area
            
        validate_input_data(input_data)
        
        # Inferir datos faltantes desde los archivos de referencia
        inferred_data = self._infer_missing_data(latitude, longitude, land_use_type, 
                                               building_type, area, value_per_m2)
        
        # Obtener función de daño
        damage_function = self._get_damage_function(
            inferred_data['land_use_type'], 
            inferred_data['building_type']
        )
        
        # Calcular ratio de daño basado en la profundidad
        damage_ratio = self._interpolate_damage_ratio(damage_function, flood_depth)
        
        # Calcular daño económico total
        total_value = inferred_data['area'] * inferred_data['value_per_m2']
        economic_damage = total_value * damage_ratio
        
        # Preparar resultados
        results = {
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'flood_parameters': {
                'depth_m': flood_depth
            },
            'property_characteristics': {
                'land_use_type': inferred_data['land_use_type'],
                'building_type': inferred_data['building_type'],
                'area_m2': inferred_data['area'],
                'value_per_m2': inferred_data['value_per_m2'],
                'total_value': total_value
            },
            'damage_assessment': {
                'damage_ratio': damage_ratio,
                'economic_damage': economic_damage,
                'currency': 'USD'
            },
            'metadata': {
                'data_sources_used': inferred_data['data_sources'],
                'calculation_method': 'depth-damage_function'
            }
        }
        
        return results
    
    def calculate_damage_batch(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcula daños para múltiples ubicaciones.
        
        Args:
            locations: Lista de diccionarios con datos de ubicaciones
            
        Returns:
            List: Lista de resultados de cálculo para cada ubicación
        """
        results = []
        
        for i, location in enumerate(locations):
            try:
                result = self.calculate_damage(**location)
                result['batch_index'] = i
                results.append(result)
            except Exception as e:
                error_result = {
                    'batch_index': i,
                    'error': str(e),
                    'location': {
                        'latitude': location.get('latitude'),
                        'longitude': location.get('longitude')
                    }
                }
                results.append(error_result)
        
        return results
    
    def _infer_missing_data(self, latitude: float, longitude: float,
                          land_use_type: Optional[str], building_type: Optional[str],
                          area: Optional[float], value_per_m2: Optional[float]) -> Dict[str, Any]:
        """
        Infiere datos faltantes usando los archivos de referencia.
        """
        data_sources = []
        
        # Inferir tipo de uso de suelo si no se proporciona
        if land_use_type is None:
            try:
                land_use_type = self.data_manager.get_land_use_at_location(latitude, longitude)
                if land_use_type:
                    data_sources.append('land_use_parquet')
                else:
                    land_use_type = 'residential'  # Valor por defecto
                    data_sources.append('default_land_use')
            except:
                land_use_type = 'residential'
                data_sources.append('default_land_use')
        
        # Inferir tipo de edificación y valor si no se proporcionan
        if building_type is None or value_per_m2 is None:
            try:
                building_info = self.data_manager.get_building_type_at_location(latitude, longitude)
                if building_info:
                    if building_type is None:
                        building_type = building_info['building_type']
                    if value_per_m2 is None:
                        value_per_m2 = building_info['value_per_m2']
                    data_sources.append('building_types_parquet')
            except:
                pass
        
        # Usar valores por defecto si aún faltan datos
        if building_type is None:
            building_type = 'single_family'
            data_sources.append('default_building_type')
        
        if value_per_m2 is None:
            value_per_m2 = self._get_default_value_per_m2(land_use_type)
            data_sources.append('default_value_per_m2')
        
        if area is None:
            area = self._default_values['default_area']
            data_sources.append('default_area')
        
        return {
            'land_use_type': land_use_type,
            'building_type': building_type,
            'area': area,
            'value_per_m2': value_per_m2,
            'data_sources': data_sources
        }
    
    def _get_default_value_per_m2(self, land_use_type: str) -> float:
        """
        Obtiene el valor por defecto por m² según el tipo de uso de suelo.
        """
        mapping = {
            'residential': self._default_values['residential_value_per_m2'],
            'commercial': self._default_values['commercial_value_per_m2'],
            'industrial': self._default_values['industrial_value_per_m2']
        }
        
        return mapping.get(land_use_type, self._default_values['residential_value_per_m2'])
    
    def _get_damage_function(self, land_use_type: str, building_type: str) -> pd.DataFrame:
        """
        Obtiene la función de daño para los tipos especificados.
        """
        try:
            damage_func = self.data_manager.get_damage_function(land_use_type, building_type)
            
            if damage_func is not None and len(damage_func) > 0:
                return damage_func
            
        except Exception:
            pass
        
        # Si no se encuentra función específica, usar función genérica
        return self._get_generic_damage_function(land_use_type)
    
    def _get_generic_damage_function(self, land_use_type: str) -> pd.DataFrame:
        """
        Genera una función de daño genérica basada en el tipo de uso de suelo.
        """
        # Funciones de daño genéricas basadas en literatura
        if land_use_type == 'residential':
            depths = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
            ratios = [0, 0.15, 0.35, 0.50, 0.65, 0.80, 0.90, 0.95]
        elif land_use_type == 'commercial':
            depths = [0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 4.0]
            ratios = [0, 0.20, 0.40, 0.60, 0.75, 0.85, 0.92, 0.97]
        elif land_use_type == 'industrial':
            depths = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
            ratios = [0, 0.10, 0.25, 0.40, 0.55, 0.70, 0.80, 0.90]
        else:
            # Función genérica para otros tipos
            depths = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
            ratios = [0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.85, 0.95]
        
        return pd.DataFrame({
            'depth': depths,
            'damage_ratio': ratios
        })
    
    def _interpolate_damage_ratio(self, damage_function: pd.DataFrame, flood_depth: float) -> float:
        """
        Interpola el ratio de daño basado en la profundidad de inundación.
        """
        if len(damage_function) < 2:
            raise CalculationError("Función de daño insuficiente para interpolación")
        
        depths = damage_function['depth'].values
        ratios = damage_function['damage_ratio'].values
        
        # Si la profundidad está fuera del rango, usar extrapolación limitada
        if flood_depth <= depths[0]:
            return ratios[0]
        elif flood_depth >= depths[-1]:
            return ratios[-1]
        
        # Interpolación lineal
        interp_func = interp1d(depths, ratios, kind='linear')
        return float(interp_func(flood_depth))
    
    def get_damage_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula estadísticas resumen para un conjunto de resultados.
        
        Args:
            results: Lista de resultados de cálculo de daños
            
        Returns:
            Dict: Estadísticas resumen
        """
        if not results:
            return {}
        
        # Filtrar resultados válidos (sin errores)
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'No hay resultados válidos para analizar'}
        
        damages = [r['damage_assessment']['economic_damage'] for r in valid_results]
        ratios = [r['damage_assessment']['damage_ratio'] for r in valid_results]
        depths = [r['flood_parameters']['depth_m'] for r in valid_results]
        
        return {
            'total_locations': len(results),
            'valid_calculations': len(valid_results),
            'failed_calculations': len(results) - len(valid_results),
            'economic_damage': {
                'total': sum(damages),
                'mean': np.mean(damages),
                'median': np.median(damages),
                'std': np.std(damages),
                'min': min(damages),
                'max': max(damages)
            },
            'damage_ratios': {
                'mean': np.mean(ratios),
                'median': np.median(ratios),
                'min': min(ratios),
                'max': max(ratios)
            },
            'flood_depths': {
                'mean': np.mean(depths),
                'median': np.median(depths),
                'min': min(depths),
                'max': max(depths)
            }
        }