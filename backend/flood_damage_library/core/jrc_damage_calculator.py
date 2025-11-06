"""
Flood damage calculator based on JRC (Joint Research Centre) data.
Uses global damage functions and maximum values by country from JRC.
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

class JRCFloodDamageCalculator:
    """
    Flood damage calculator based on JRC data.
    
    Features:
    - Damage functions by region (Europe, North America, Asia, etc.)
    - Maximum damage values by country and building type
    - Support for multiple building types (residential, commercial, industrial)
    - Uncertainty analysis with standard deviations
    """
    
    def __init__(self, data_directory: str = "./processed_jrc_data"):
        """
        Initialize the JRC calculator.
        
        Args:
            data_directory: Directory with processed JRC data
        """
        self.data_directory = Path(data_directory)
        self.logger = logging.getLogger(__name__)
        
        # Load JRC data
        self._load_jrc_data()
        
        # Region to country mapping (simplified)
        self.region_mapping = {
            'EUROPE': ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'SE', 'NO', 'DK', 'FI', 'PL', 'CZ', 'HU', 'RO', 'BG', 'GR', 'PT', 'IE', 'LU', 'SK', 'SI', 'EE', 'LV', 'LT', 'CY', 'MT', 'HR', 'GB', 'IS', 'LI', 'MC', 'SM', 'VA', 'AD', 'AL', 'BA', 'ME', 'MK', 'RS', 'XK', 'MD', 'UA', 'BY', 'RU'],
            'North AMERICA': ['US', 'CA', 'MX', 'GT', 'BZ', 'SV', 'HN', 'NI', 'CR', 'PA'],
            'Centr&South_AMERICA': ['BR', 'AR', 'CL', 'PE', 'CO', 'VE', 'EC', 'BO', 'PY', 'UY', 'GY', 'SR', 'GF'],
            'ASIA': ['CN', 'IN', 'JP', 'KR', 'TH', 'VN', 'MY', 'SG', 'ID', 'PH', 'BD', 'PK', 'LK', 'MM', 'KH', 'LA', 'BN', 'TL', 'MN', 'KZ', 'UZ', 'TM', 'TJ', 'KG', 'AF', 'IR', 'IQ', 'SY', 'JO', 'LB', 'IL', 'PS', 'SA', 'YE', 'OM', 'AE', 'QA', 'BH', 'KW', 'TR', 'GE', 'AM', 'AZ'],
            'AFRICA': ['NG', 'ET', 'EG', 'ZA', 'KE', 'UG', 'DZ', 'SD', 'MA', 'AO', 'GH', 'MZ', 'MG', 'CM', 'CI', 'NE', 'BF', 'ML', 'MW', 'ZM', 'SO', 'SN', 'TD', 'ZW', 'GN', 'RW', 'BJ', 'TN', 'BI', 'ER', 'SL', 'TG', 'CF', 'LY', 'LR', 'MR', 'GA', 'BW', 'LS', 'GQ', 'GM', 'GW', 'SZ', 'DJ', 'KM', 'CV', 'ST', 'SC', 'MU'],
            'OCEANIA': ['AU', 'NZ', 'PG', 'FJ', 'SB', 'NC', 'PF', 'VU', 'WS', 'KI', 'FM', 'TO', 'MH', 'PW', 'CK', 'NU', 'TK', 'TV', 'NR', 'AS', 'GU', 'MP', 'VI', 'PR', 'UM']
        }
    
    def _load_jrc_data(self):
        """Load processed JRC data."""
        try:
            # Load damage functions
            damage_func_file = self.data_directory / 'damage_functions_jrc.parquet'
            if damage_func_file.exists():
                try:
                    self.damage_functions = pd.read_parquet(damage_func_file, engine='pyarrow')
                except Exception as e:
                    # Fallback to fastparquet if pyarrow fails
                    try:
                        self.damage_functions = pd.read_parquet(damage_func_file, engine='fastparquet')
                    except Exception:
                        # Final fallback - recreate from CSV if available
                        csv_file = self.data_directory / 'damage_functions_jrc.csv'
                        if csv_file.exists():
                            self.damage_functions = pd.read_csv(csv_file)
                        else:
                            raise e
                print(f"✅ JRC damage functions loaded: {len(self.damage_functions)} records")
            else:
                raise FileNotFoundError(f"File not found: {damage_func_file}")
            
            # Load maximum damage values
            self.max_damage_data = {}
            
            for building_type in ['residential', 'commercial', 'industrial', 'agriculture', 'infrastructure', 'transport']:
                file_path = self.data_directory / f'max_damage_{building_type}_jrc.parquet'
                if file_path.exists():
                    try:
                        self.max_damage_data[building_type] = pd.read_parquet(file_path, engine='pyarrow')
                    except Exception:
                        try:
                            self.max_damage_data[building_type] = pd.read_parquet(file_path, engine='fastparquet')
                        except Exception:
                            # Skip if can't load
                            continue
                    print(f"✅ Maximum {building_type} values loaded: {len(self.max_damage_data[building_type])} countries")
            
            # Load ISO table
            iso_file = self.data_directory / 'iso_table_jrc.parquet'
            if iso_file.exists():
                try:
                    self.iso_table = pd.read_parquet(iso_file, engine='pyarrow')
                except Exception:
                    try:
                        self.iso_table = pd.read_parquet(iso_file, engine='fastparquet')
                    except Exception:
                        self.iso_table = pd.DataFrame()
                print(f"✅ ISO table loaded: {len(self.iso_table)} countries")
            else:
                self.iso_table = pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error loading JRC data: {e}")
            raise CalculationError(f"Could not load JRC data: {e}")
    
    def calculate_jrc_damage(self,
                           latitude: Optional[float] = None,
                           longitude: Optional[float] = None,
                           flood_depth: float = None,
                           country_code: Optional[str] = None,
                           building_type: str = 'residential',
                           area_m2: Optional[float] = None,
                           region: Optional[str] = None,
                           **kwargs) -> Dict:
        """
        Calculate damage using JRC functions.
        
        Args:
            latitude: Location latitude (optional, used for country inference if country_code not provided)
            longitude: Location longitude (optional, used for country inference if country_code not provided)
            flood_depth: Flood depth in meters (required)
            country_code: ISO country code (e.g., 'US', 'DE', 'BR') - required if coordinates not provided
            building_type: Building type ('residential', 'commercial', 'industrial')
            area_m2: Affected area in square meters
            region: Specific region to use (optional, inferred from country if not provided)
            
        Returns:
            Dictionary with detailed results
        """
        # Validate required inputs
        if flood_depth is None:
            raise DataValidationError("flood_depth is required")
        
        validate_flood_depth(flood_depth)
        
        valid_building_types = ['residential', 'commercial', 'industrial', 'agriculture', 'infrastructure', 'transport']
        if building_type not in valid_building_types:
            raise DataValidationError(f"Unsupported building type: {building_type}. Valid types: {valid_building_types}")
        
        # Validate coordinates if provided
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise DataValidationError("Both latitude and longitude must be provided if using coordinates")
            validate_coordinates(latitude, longitude)
        
        # Infer country and region if not provided
        if not country_code:
            if latitude is not None and longitude is not None:
                country_code = self._infer_country_from_coordinates(latitude, longitude)
            else:
                raise DataValidationError("Either coordinates (latitude, longitude) or country_code must be provided")
        
        if not region:
            region = self._get_region_for_country(country_code)
        
        # Get damage function
        damage_ratio = self._get_jrc_damage_ratio(flood_depth, building_type, region)
        
        # Get maximum damage values for the country
        max_damage_data = self._get_max_damage_for_country(country_code, building_type)
        
        # Calculate area (use default value if not provided)
        if not area_m2:
            area_m2 = 100  # 100 m² default
        
        # Calculate economic damage
        max_damage_per_m2 = max_damage_data.get('total_building_eur_m2', 500)  # EUR/m² default
        total_value = area_m2 * max_damage_per_m2
        economic_damage = total_value * damage_ratio
        
        # Get country information
        country_info = self._get_country_info(country_code)
        
        # Uncertainty analysis
        uncertainty_analysis = self._calculate_jrc_uncertainty(
            economic_damage, damage_ratio, building_type, region
        )
        
        # Build result
        location_info = {
            'country_code': country_code,
            'country_name': country_info.get('country_name', 'Unknown'),
            'region': region
        }
        
        # Add coordinates only if provided
        if latitude is not None and longitude is not None:
            location_info['latitude'] = latitude
            location_info['longitude'] = longitude
        
        result = {
            'location': location_info,
            'flood_parameters': {
                'depth_m': flood_depth
            },
            'property_characteristics': {
                'building_type': building_type,
                'area_m2': area_m2,
                'max_damage_per_m2_eur': max_damage_per_m2,
                'total_value_eur': total_value,
                'currency': 'EUR',
                'base_year': 2010
            },
            'damage_assessment': {
                'damage_ratio': damage_ratio,
                'economic_damage_eur': economic_damage,
                'currency': 'EUR'
            },
            'jrc_data': {
                'region_used': region,
                'max_damage_structure': max_damage_data.get('max_damage_structure_eur_m2'),
                'max_damage_content': max_damage_data.get('max_damage_content_eur_m2'),
                'data_source': 'JRC Global Flood Depth-Damage Functions Database'
            },
            'uncertainty_analysis': uncertainty_analysis,
            'metadata': {
                'calculation_method': 'jrc_depth_damage_function',
                'data_version': 'JRC 2017',
                'includes_uncertainty': True
            }
        }
        
        return result
    
    def calculate_damage_by_country(self,
                                   flood_depth: float,
                                   country_code: str,
                                   building_type: str = 'residential',
                                   area_m2: Optional[float] = None,
                                   region: Optional[str] = None) -> Dict:
        """
        Calculate damage using country code directly (no coordinates needed).
        
        Args:
            flood_depth: Flood depth in meters
            country_code: ISO country code (e.g., 'US', 'DE', 'BR')
            building_type: Building type ('residential', 'commercial', 'industrial')
            area_m2: Affected area in square meters
            region: Specific region to use (optional, inferred from country if not provided)
            
        Returns:
            Dictionary with detailed results
        """
        return self.calculate_jrc_damage(
            latitude=None,
            longitude=None,
            flood_depth=flood_depth,
            country_code=country_code,
            building_type=building_type,
            area_m2=area_m2,
            region=region
        )
    
    def _get_jrc_damage_ratio(self, depth: float, building_type: str, region: str) -> float:
        """Get damage ratio using JRC functions."""
        
        # Map building type to JRC damage class
        building_type_mapping = {
            'residential': 'residential_buildings',
            'commercial': 'commercial_buildings', 
            'industrial': 'industrial_buildings',
            'agriculture': 'agriculture',
            'infrastructure': 'infrastructure___roads',
            'transport': 'transport'
        }
        
        damage_class = building_type_mapping.get(building_type, 'residential_buildings')
        
        # Filter damage functions
        mask = (
            (self.damage_functions['building_type'] == damage_class) &
            (self.damage_functions['region'] == region)
        )
        
        relevant_functions = self.damage_functions[mask]
        
        if relevant_functions.empty:
            # Try with GLOBAL region
            mask_global = (
                (self.damage_functions['building_type'] == damage_class) &
                (self.damage_functions['region'] == 'GLOBAL')
            )
            relevant_functions = self.damage_functions[mask_global]
        
        if relevant_functions.empty:
            # Usar función genérica
            return min(1.0, depth * 0.3)  # 30% de daño por metro
        
        # Obtener datos para interpolación
        depths = relevant_functions['depth_m'].values
        ratios = relevant_functions['damage_ratio'].values
        
        if len(depths) == 1:
            return ratios[0]
        
        # Ordenar por profundidad
        sorted_indices = np.argsort(depths)
        depths_sorted = depths[sorted_indices]
        ratios_sorted = ratios[sorted_indices]
        
        # Interpolación lineal
        if depth <= depths_sorted[0]:
            return ratios_sorted[0]
        elif depth >= depths_sorted[-1]:
            return ratios_sorted[-1]
        else:
            return np.interp(depth, depths_sorted, ratios_sorted)
    
    def _get_max_damage_for_country(self, country_code: str, building_type: str) -> Dict:
        """Obtiene los valores máximos de daño para un país y tipo de edificación."""
        
        if building_type not in self.max_damage_data:
            return {'total_building_eur_m2': 500}  # Valor por defecto
        
        # Buscar por código de país
        country_data = self.max_damage_data[building_type][
            self.max_damage_data[building_type]['country'].str.upper() == country_code.upper()
        ]
        
        if country_data.empty:
            # Buscar por nombre de país en tabla ISO
            country_name = self._get_country_name_from_code(country_code)
            if country_name:
                country_data = self.max_damage_data[building_type][
                    self.max_damage_data[building_type]['country'].str.upper() == country_name.upper()
                ]
        
        if not country_data.empty:
            return country_data.iloc[0].to_dict()
        else:
            # Default values based on building type
            defaults = {
                'residential': {'total_building_eur_m2': 400},
                'commercial': {'total_building_eur_m2': 600},
                'industrial': {'total_building_eur_m2': 500},
                'agriculture': {'total_building_eur_m2': 50},  # Lower value for agricultural land
                'infrastructure': {'total_building_eur_m2': 25},  # Infrastructure damage per m2
                'transport': {'total_building_eur_m2': 750}  # Transport infrastructure
            }
            return defaults.get(building_type, {'total_building_eur_m2': 500})
    
    def _get_region_for_country(self, country_code: str) -> str:
        """Determina la región JRC para un código de país."""
        
        for region, countries in self.region_mapping.items():
            if country_code.upper() in [c.upper() for c in countries]:
                return region
        
        # Si no se encuentra, usar región global
        return 'GLOBAL'
    
    def _infer_country_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Infiere el país basándose en coordenadas geográficas (simplificado)."""
        
        # Reglas geográficas básicas
        if 25 <= latitude <= 49 and -125 <= longitude <= -66:
            return 'US'
        elif 14 <= latitude <= 33 and -118 <= longitude <= -86:
            return 'MX'
        elif 42 <= latitude <= 70 and -141 <= longitude <= -52:
            return 'CA'
        elif -34 <= latitude <= 5 and -74 <= longitude <= -35:
            return 'BR'
        elif 36 <= latitude <= 71 and -10 <= longitude <= 40:
            return 'DE'  # Europa central como ejemplo
        elif 20 <= latitude <= 50 and 70 <= longitude <= 140:
            return 'CN'  # Asia
        elif -35 <= latitude <= 37 and 110 <= longitude <= 155:
            return 'AU'  # Oceanía
        else:
            return 'US'  # Por defecto
    
    def _get_country_info(self, country_code: str) -> Dict:
        """Obtiene información del país desde la tabla ISO."""
        
        if self.iso_table.empty:
            return {'country_name': 'Unknown'}
        
        # Buscar por código ISO
        country_info = self.iso_table[
            (self.iso_table['iso_alpha2'].str.upper() == country_code.upper()) |
            (self.iso_table['iso_alpha3'].str.upper() == country_code.upper())
        ]
        
        if not country_info.empty:
            return country_info.iloc[0].to_dict()
        else:
            return {'country_name': 'Unknown'}
    
    def _get_country_name_from_code(self, country_code: str) -> Optional[str]:
        """Obtiene el nombre del país desde el código ISO."""
        
        country_info = self._get_country_info(country_code)
        return country_info.get('country_name')
    
    def _calculate_jrc_uncertainty(self, economic_damage: float, damage_ratio: float, 
                                 building_type: str, region: str) -> Dict:
        """Calcula análisis de incertidumbre usando datos del JRC."""
        
        # Buscar desviación estándar en los datos JRC
        building_type_mapping = {
            'residential': 'Residential buildings',
            'commercial': 'Commercial buildings', 
            'industrial': 'Industrial buildings'
        }
        
        damage_class = building_type_mapping.get(building_type, 'Residential buildings')
        
        # Filtrar datos de incertidumbre
        uncertainty_data = self.damage_functions[
            (self.damage_functions['damage_class'] == damage_class) &
            (self.damage_functions['region'] == region) &
            (self.damage_functions['standard_deviation'].notna())
        ]
        
        if uncertainty_data.empty:
            # Usar valores por defecto
            std_dev = 0.2  # 20% de incertidumbre
        else:
            # Usar promedio de desviaciones estándar disponibles
            std_dev = uncertainty_data['standard_deviation'].mean()
        
        # Calcular intervalos de confianza
        damage_std = economic_damage * std_dev
        
        return {
            'standard_deviation_ratio': std_dev,
            'damage_standard_deviation_eur': damage_std,
            'confidence_interval_95': {
                'lower_eur': max(0, economic_damage - 1.96 * damage_std),
                'upper_eur': economic_damage + 1.96 * damage_std
            },
            'confidence_interval_68': {
                'lower_eur': max(0, economic_damage - damage_std),
                'upper_eur': economic_damage + damage_std
            },
            'data_source': 'JRC standard deviations'
        }
    
    def calculate_damage_batch_jrc(self, locations: List[Dict]) -> List[Dict]:
        """
        Calcula daños para múltiples ubicaciones usando datos JRC.
        
        Args:
            locations: Lista de diccionarios con datos de ubicación
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for i, location in enumerate(locations):
            try:
                result = self.calculate_jrc_damage(
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    flood_depth=location['flood_depth'],
                    country_code=location.get('country_code'),
                    building_type=location.get('building_type', 'residential'),
                    area_m2=location.get('area_m2'),
                    region=location.get('region'),
                    **{k: v for k, v in location.items() 
                       if k not in ['latitude', 'longitude', 'flood_depth', 'country_code', 'building_type', 'area_m2', 'region']}
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
    
    def get_available_regions(self) -> List[str]:
        """Get list of available regions in the JRC data."""
        if hasattr(self, 'damage_functions') and not self.damage_functions.empty:
            return sorted(self.damage_functions['region'].unique().tolist())
        return ['EUROPE', 'North AMERICA', 'Centr&South_AMERICA', 'ASIA', 'AFRICA', 'OCEANIA', 'GLOBAL']
    
    def get_available_building_types(self) -> List[str]:
        """Get list of available building types."""
        return ['residential', 'commercial', 'industrial', 'agriculture', 'infrastructure', 'transport']
    
    def get_countries_with_data(self, building_type: str = 'residential') -> List[str]:
        """Get list of countries with maximum damage data for the specified building type."""
        if building_type in self.max_damage_data:
            return sorted(self.max_damage_data[building_type]['country'].unique().tolist())
        return []
    
    def calculate_damage_batch_by_country(self, scenarios: List[Dict]) -> List[Dict]:
        """
        Calculate flood damage for multiple scenarios using country codes (no coordinates needed).
        
        This function processes multiple damage calculations in batch using only country codes,
        making it ideal for portfolio analysis, risk assessment across countries, or 
        scenario analysis without needing precise coordinates.
        
        Args:
            scenarios: List of dictionaries with scenario data. Each dictionary should contain:
                - flood_depth (float): Flood depth in meters (required)
                - country_code (str): ISO country code like 'US', 'DE', 'BR' (required)
                - building_type (str, optional): Building type, default 'residential'
                - area_m2 (float, optional): Area in square meters, default 100
                - region (str, optional): JRC region, auto-inferred if not provided
                - Any additional parameters for the calculation
                
        Returns:
            List[Dict]: List of calculation results, each containing:
                - batch_index: Index in the original scenarios list
                - All standard calculation results (damage_assessment, uncertainty_analysis, etc.)
                - Or error information if calculation failed
                
        Example:
            ```python
            calculator = JRCFloodDamageCalculator()
            
            scenarios = [
                {
                    'flood_depth': 1.5,
                    'country_code': 'DE',
                    'building_type': 'residential',
                    'area_m2': 120
                },
                {
                    'flood_depth': 2.0,
                    'country_code': 'FR',
                    'building_type': 'commercial',
                    'area_m2': 500
                },
                {
                    'flood_depth': 1.0,
                    'country_code': 'IT',
                    'building_type': 'industrial',
                    'area_m2': 1000
                }
            ]
            
            results = calculator.calculate_damage_batch_by_country(scenarios)
            
            for result in results:
                if 'error' not in result:
                    damage = result['damage_assessment']['economic_damage_eur']
                    print(f"Scenario {result['batch_index']}: €{damage:,.0f}")
                else:
                    print(f"Scenario {result['batch_index']}: Error - {result['error']}")
            ```
        """
        results = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Validate required parameters
                if 'flood_depth' not in scenario:
                    raise DataValidationError("flood_depth is required for each scenario")
                if 'country_code' not in scenario:
                    raise DataValidationError("country_code is required for each scenario")
                
                # Calculate damage using country-based method
                result = self.calculate_damage_by_country(
                    flood_depth=scenario['flood_depth'],
                    country_code=scenario['country_code'],
                    building_type=scenario.get('building_type', 'residential'),
                    area_m2=scenario.get('area_m2', 100),
                    region=scenario.get('region')
                )
                
                # Add batch information
                result['batch_index'] = i
                result['input_scenario'] = {
                    'flood_depth': scenario['flood_depth'],
                    'country_code': scenario['country_code'],
                    'building_type': scenario.get('building_type', 'residential'),
                    'area_m2': scenario.get('area_m2', 100)
                }
                
                results.append(result)
                
            except Exception as e:
                # Handle errors gracefully
                error_result = {
                    'batch_index': i,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'input_scenario': {
                        'flood_depth': scenario.get('flood_depth'),
                        'country_code': scenario.get('country_code'),
                        'building_type': scenario.get('building_type', 'residential'),
                        'area_m2': scenario.get('area_m2', 100)
                    }
                }
                results.append(error_result)
                
                # Log the error for debugging
                self.logger.warning(f"Batch calculation failed for scenario {i}: {str(e)}")
        
        return results
