"""
Calculadora de daños por inundación mejorada que incluye:
- Funciones de daño por país/región
- Datos económicos (PIB) para ajustes
- Análisis de incertidumbre con desviaciones estándar
- Soporte para códigos ISO de países
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from scipy import interpolate
from ..utils.validators import validate_coordinates, validate_flood_depth
from ..utils.exceptions import DataValidationError, CalculationError
from .data_manager import DataManager

class EnhancedFloodDamageCalculator:
    """
    Calculadora avanzada de daños por inundación con soporte para:
    - Funciones de daño específicas por país/región
    - Ajustes económicos basados en PIB
    - Análisis de incertidumbre
    - Códigos ISO de países
    """
    
    def __init__(self, data_directory: str = "./data"):
        """
        Inicializa la calculadora mejorada.
        
        Args:
            data_directory: Directorio con archivos de datos
        """
        self.data_manager = DataManager(data_directory)
        self.logger = logging.getLogger(__name__)
        
        # Valores por defecto mejorados
        self._default_values = {
            'area_m2': 100,
            'building_type': 'residential',
            'country_code': 'US',
            'currency': 'USD',
            'base_value_per_m2': 1000,
            'uncertainty_factor': 0.2  # 20% de incertidumbre por defecto
        }
        
        # Cargar datos específicos si están disponibles
        self._load_enhanced_data()
    
    def _load_enhanced_data(self):
        """Carga datos específicos para cálculos mejorados."""
        try:
            # Intentar cargar funciones de daño específicas
            self.damage_functions = self._load_damage_functions()
            
            # Intentar cargar datos de países y PIB
            self.country_data = self._load_country_data()
            
            # Intentar cargar tabla ISO
            self.iso_table = self._load_iso_table()
            
            # Intentar cargar datos de incertidumbre
            self.uncertainty_data = self._load_uncertainty_data()
            
        except Exception as e:
            self.logger.warning(f"No se pudieron cargar todos los datos específicos: {e}")
            self._create_fallback_data()
    
    def _load_damage_functions(self) -> pd.DataFrame:
        """Carga funciones de daño específicas."""
        try:
            return self.data_manager.load_parquet_file('damage_functions_data.parquet')
        except:
            # Crear funciones de daño por defecto
            return self._create_default_damage_functions()
    
    def _load_country_data(self) -> pd.DataFrame:
        """Carga datos de países y PIB."""
        try:
            return self.data_manager.load_parquet_file('countries_gdp_data.parquet')
        except:
            return self._create_default_country_data()
    
    def _load_iso_table(self) -> pd.DataFrame:
        """Carga tabla de códigos ISO."""
        try:
            return self.data_manager.load_parquet_file('iso_table_data.parquet')
        except:
            return self._create_default_iso_table()
    
    def _load_uncertainty_data(self) -> pd.DataFrame:
        """Carga datos de incertidumbre."""
        try:
            return self.data_manager.load_parquet_file('standard_deviation_data_cleaned.parquet')
        except:
            return self._create_default_uncertainty_data()
    
    def _create_fallback_data(self):
        """Crea datos de respaldo cuando no se pueden cargar los archivos."""
        self.damage_functions = self._create_default_damage_functions()
        self.country_data = self._create_default_country_data()
        self.iso_table = self._create_default_iso_table()
        self.uncertainty_data = self._create_default_uncertainty_data()
    
    def _create_default_damage_functions(self) -> pd.DataFrame:
        """Crea funciones de daño por defecto."""
        building_types = ['residential', 'commercial', 'industrial', 'institutional']
        depths = np.arange(0, 6, 0.5)
        
        data = []
        for building_type in building_types:
            for depth in depths:
                # Función de daño sigmoidea
                if building_type == 'residential':
                    damage_ratio = min(1.0, 1 / (1 + np.exp(-2 * (depth - 1.5))))
                elif building_type == 'commercial':
                    damage_ratio = min(1.0, 1 / (1 + np.exp(-2.5 * (depth - 1.2))))
                elif building_type == 'industrial':
                    damage_ratio = min(1.0, 1 / (1 + np.exp(-1.8 * (depth - 1.8))))
                else:  # institutional
                    damage_ratio = min(1.0, 1 / (1 + np.exp(-2.2 * (depth - 1.4))))
                
                data.append({
                    'building_type': building_type,
                    'depth_m': depth,
                    'damage_ratio': damage_ratio,
                    'country_code': 'DEFAULT'
                })
        
        return pd.DataFrame(data)
    
    def _create_default_country_data(self) -> pd.DataFrame:
        """Crea datos de países por defecto."""
        countries = [
            {'country_code': 'US', 'country_name': 'United States', 'gdp_per_capita': 65000, 'currency': 'USD'},
            {'country_code': 'MX', 'country_name': 'Mexico', 'gdp_per_capita': 10000, 'currency': 'MXN'},
            {'country_code': 'CA', 'country_name': 'Canada', 'gdp_per_capita': 50000, 'currency': 'CAD'},
            {'country_code': 'BR', 'country_name': 'Brazil', 'gdp_per_capita': 8500, 'currency': 'BRL'},
            {'country_code': 'DEFAULT', 'country_name': 'Default', 'gdp_per_capita': 25000, 'currency': 'USD'}
        ]
        return pd.DataFrame(countries)
    
    def _create_default_iso_table(self) -> pd.DataFrame:
        """Crea tabla ISO por defecto."""
        iso_data = [
            {'iso_alpha2': 'US', 'iso_alpha3': 'USA', 'country_name': 'United States', 'numeric_code': 840},
            {'iso_alpha2': 'MX', 'iso_alpha3': 'MEX', 'country_name': 'Mexico', 'numeric_code': 484},
            {'iso_alpha2': 'CA', 'iso_alpha3': 'CAN', 'country_name': 'Canada', 'numeric_code': 124},
            {'iso_alpha2': 'BR', 'iso_alpha3': 'BRA', 'country_name': 'Brazil', 'numeric_code': 76}
        ]
        return pd.DataFrame(iso_data)
    
    def _create_default_uncertainty_data(self) -> pd.DataFrame:
        """Crea datos de incertidumbre por defecto."""
        building_types = ['residential', 'commercial', 'industrial', 'institutional']
        data = []
        
        for building_type in building_types:
            # Diferentes niveles de incertidumbre por tipo de edificación
            if building_type == 'residential':
                std_dev = 0.15  # 15% de desviación estándar
            elif building_type == 'commercial':
                std_dev = 0.20  # 20% de desviación estándar
            elif building_type == 'industrial':
                std_dev = 0.25  # 25% de desviación estándar
            else:  # institutional
                std_dev = 0.18  # 18% de desviación estándar
            
            data.append({
                'building_type': building_type,
                'standard_deviation': std_dev,
                'confidence_interval_95': std_dev * 1.96
            })
        
        return pd.DataFrame(data)
    
    def calculate_enhanced_damage(self, 
                                latitude: float,
                                longitude: float,
                                flood_depth: float,
                                country_code: Optional[str] = None,
                                building_type: Optional[str] = None,
                                area: Optional[float] = None,
                                include_uncertainty: bool = True,
                                **kwargs) -> Dict:
        """
        Calcula daños con funcionalidades mejoradas.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            flood_depth: Profundidad de inundación en metros
            country_code: Código de país (ISO Alpha-2)
            building_type: Tipo de edificación
            area: Área afectada en m²
            include_uncertainty: Si incluir análisis de incertidumbre
            **kwargs: Parámetros adicionales
            
        Returns:
            Diccionario con resultados detallados
        """
        # Validar entrada
        validate_coordinates(latitude, longitude)
        validate_flood_depth(flood_depth)
        
        # Inferir datos faltantes
        inferred_data = self._infer_location_data(latitude, longitude, country_code, building_type)
        
        # Obtener función de daño
        damage_ratio = self._get_damage_ratio(
            flood_depth, 
            inferred_data['building_type'],
            inferred_data['country_code']
        )
        
        # Obtener datos económicos
        economic_data = self._get_economic_data(inferred_data['country_code'])
        
        # Calcular área y valor
        area_m2 = area or self._default_values['area_m2']
        value_per_m2 = self._calculate_adjusted_value_per_m2(economic_data)
        total_value = area_m2 * value_per_m2
        
        # Calcular daño económico
        economic_damage = total_value * damage_ratio
        
        # Análisis de incertidumbre
        uncertainty_analysis = None
        if include_uncertainty:
            uncertainty_analysis = self._calculate_uncertainty(
                economic_damage, 
                inferred_data['building_type'],
                damage_ratio
            )
        
        # Construir resultado
        result = {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'country_code': inferred_data['country_code'],
                'country_name': economic_data.get('country_name', 'Unknown')
            },
            'flood_parameters': {
                'depth_m': flood_depth
            },
            'property_characteristics': {
                'building_type': inferred_data['building_type'],
                'area_m2': area_m2,
                'value_per_m2': value_per_m2,
                'total_value': total_value,
                'currency': economic_data.get('currency', 'USD')
            },
            'damage_assessment': {
                'damage_ratio': damage_ratio,
                'economic_damage': economic_damage,
                'currency': economic_data.get('currency', 'USD')
            },
            'economic_context': {
                'gdp_per_capita': economic_data.get('gdp_per_capita', 25000),
                'economic_adjustment_factor': self._calculate_economic_adjustment(economic_data)
            },
            'metadata': {
                'calculation_method': 'enhanced_depth_damage_function',
                'data_sources': ['damage_functions', 'country_data', 'iso_table'],
                'includes_uncertainty': include_uncertainty
            }
        }
        
        if uncertainty_analysis:
            result['uncertainty_analysis'] = uncertainty_analysis
        
        return result
    
    def _infer_location_data(self, latitude: float, longitude: float, 
                           country_code: Optional[str], 
                           building_type: Optional[str]) -> Dict:
        """Infiere datos de ubicación basándose en coordenadas."""
        
        # Si no se proporciona código de país, intentar inferir por ubicación
        if not country_code:
            country_code = self._infer_country_from_coordinates(latitude, longitude)
        
        # Si no se proporciona tipo de edificación, usar por defecto
        if not building_type:
            building_type = self._default_values['building_type']
        
        return {
            'country_code': country_code,
            'building_type': building_type
        }
    
    def _infer_country_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Infiere el país basándose en coordenadas geográficas."""
        # Reglas simples basadas en rangos geográficos
        if 25 <= latitude <= 49 and -125 <= longitude <= -66:
            return 'US'  # Estados Unidos continental
        elif 14 <= latitude <= 33 and -118 <= longitude <= -86:
            return 'MX'  # México
        elif 42 <= latitude <= 70 and -141 <= longitude <= -52:
            return 'CA'  # Canadá
        elif -34 <= latitude <= 5 and -74 <= longitude <= -35:
            return 'BR'  # Brasil
        else:
            return 'DEFAULT'
    
    def _get_damage_ratio(self, depth: float, building_type: str, country_code: str) -> float:
        """Obtiene el ratio de daño para los parámetros dados."""
        # Filtrar funciones de daño
        mask = (
            (self.damage_functions['building_type'] == building_type) &
            (self.damage_functions['country_code'].isin([country_code, 'DEFAULT']))
        )
        
        relevant_functions = self.damage_functions[mask]
        
        if relevant_functions.empty:
            # Usar función genérica
            return min(1.0, depth * 0.3)  # 30% de daño por metro
        
        # Preferir datos específicos del país
        country_specific = relevant_functions[relevant_functions['country_code'] == country_code]
        if not country_specific.empty:
            relevant_functions = country_specific
        
        # Interpolación
        depths = relevant_functions['depth_m'].values
        ratios = relevant_functions['damage_ratio'].values
        
        if len(depths) == 1:
            return ratios[0]
        
        # Interpolación lineal
        f = interpolate.interp1d(depths, ratios, kind='linear', 
                               bounds_error=False, fill_value=(ratios[0], ratios[-1]))
        
        return float(f(depth))
    
    def _get_economic_data(self, country_code: str) -> Dict:
        """Obtiene datos económicos para un país."""
        country_data = self.country_data[self.country_data['country_code'] == country_code]
        
        if country_data.empty:
            # Usar datos por defecto
            country_data = self.country_data[self.country_data['country_code'] == 'DEFAULT']
        
        if not country_data.empty:
            return country_data.iloc[0].to_dict()
        else:
            return {
                'country_name': 'Unknown',
                'gdp_per_capita': 25000,
                'currency': 'USD'
            }
    
    def _calculate_adjusted_value_per_m2(self, economic_data: Dict) -> float:
        """Calcula valor por m² ajustado por contexto económico."""
        base_value = self._default_values['base_value_per_m2']
        gdp_per_capita = economic_data.get('gdp_per_capita', 25000)
        
        # Ajuste basado en PIB per cápita (usando US como referencia)
        us_gdp_per_capita = 65000
        adjustment_factor = gdp_per_capita / us_gdp_per_capita
        
        return base_value * adjustment_factor
    
    def _calculate_economic_adjustment(self, economic_data: Dict) -> float:
        """Calcula factor de ajuste económico."""
        gdp_per_capita = economic_data.get('gdp_per_capita', 25000)
        us_gdp_per_capita = 65000
        return gdp_per_capita / us_gdp_per_capita
    
    def _calculate_uncertainty(self, economic_damage: float, building_type: str, damage_ratio: float) -> Dict:
        """Calcula análisis de incertidumbre."""
        # Obtener desviación estándar para el tipo de edificación
        uncertainty_data = self.uncertainty_data[
            self.uncertainty_data['building_type'] == building_type
        ]
        
        if uncertainty_data.empty:
            std_dev = self._default_values['uncertainty_factor']
        else:
            std_dev = uncertainty_data.iloc[0]['standard_deviation']
        
        # Calcular intervalos de confianza
        damage_std = economic_damage * std_dev
        
        return {
            'standard_deviation': std_dev,
            'damage_standard_deviation': damage_std,
            'confidence_interval_95': {
                'lower': max(0, economic_damage - 1.96 * damage_std),
                'upper': economic_damage + 1.96 * damage_std
            },
            'confidence_interval_68': {
                'lower': max(0, economic_damage - damage_std),
                'upper': economic_damage + damage_std
            }
        }
    
    def calculate_damage_batch_enhanced(self, locations: List[Dict], 
                                      include_uncertainty: bool = True) -> List[Dict]:
        """
        Calcula daños para múltiples ubicaciones con funcionalidades mejoradas.
        
        Args:
            locations: Lista de diccionarios con datos de ubicación
            include_uncertainty: Si incluir análisis de incertidumbre
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, location in enumerate(locations):
            try:
                result = self.calculate_enhanced_damage(
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    flood_depth=location['flood_depth'],
                    country_code=location.get('country_code'),
                    building_type=location.get('building_type'),
                    area=location.get('area'),
                    include_uncertainty=include_uncertainty,
                    **{k: v for k, v in location.items() 
                       if k not in ['latitude', 'longitude', 'flood_depth', 'country_code', 'building_type', 'area']}
                )
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
    
    def get_enhanced_summary_statistics(self, results: List[Dict]) -> Dict:
        """
        Calcula estadísticas resumen mejoradas para un conjunto de resultados.
        
        Args:
            results: Lista de resultados de cálculos
            
        Returns:
            Diccionario con estadísticas resumen
        """
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'No hay resultados válidos para analizar'}
        
        # Extraer datos económicos
        damages = [r['damage_assessment']['economic_damage'] for r in valid_results]
        ratios = [r['damage_assessment']['damage_ratio'] for r in valid_results]
        countries = [r['location']['country_code'] for r in valid_results]
        building_types = [r['property_characteristics']['building_type'] for r in valid_results]
        
        # Estadísticas básicas
        stats = {
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
            'damage_ratio': {
                'mean': np.mean(ratios),
                'median': np.median(ratios),
                'std': np.std(ratios),
                'min': min(ratios),
                'max': max(ratios)
            },
            'geographic_distribution': {
                'countries': list(set(countries)),
                'country_counts': {country: countries.count(country) for country in set(countries)}
            },
            'building_type_distribution': {
                'types': list(set(building_types)),
                'type_counts': {bt: building_types.count(bt) for bt in set(building_types)}
            }
        }
        
        # Análisis de incertidumbre agregado
        uncertainty_data = []
        for result in valid_results:
            if 'uncertainty_analysis' in result:
                uncertainty_data.append(result['uncertainty_analysis'])
        
        if uncertainty_data:
            ci_95_lowers = [u['confidence_interval_95']['lower'] for u in uncertainty_data]
            ci_95_uppers = [u['confidence_interval_95']['upper'] for u in uncertainty_data]
            
            stats['uncertainty_analysis'] = {
                'total_with_uncertainty': len(uncertainty_data),
                'aggregate_confidence_interval_95': {
                    'lower': sum(ci_95_lowers),
                    'upper': sum(ci_95_uppers)
                },
                'mean_uncertainty_range': np.mean([u - l for l, u in zip(ci_95_lowers, ci_95_uppers)])
            }
        
        return stats