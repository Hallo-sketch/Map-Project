# src/cleaning/geo_utils.py
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import json
from pathlib import Path

class GeoDataHandler:
    """Utility class for handling geospatial data in the cocoa dashboard."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def read_geojson(self, filename: str) -> gpd.GeoDataFrame:
        """
        Read and validate a GeoJSON file.
        
        Parameters:
        -----------
        filename : str
            Name of the GeoJSON file in the data directory
            
        Returns:
        --------
        gpd.GeoDataFrame
            Geodataframe containing the spatial data
        """
        filepath = self.data_dir / filename
        try:
            gdf = gpd.read_file(filepath)
            print(f"Successfully loaded GeoJSON with {len(gdf)} features")
            print(f"CRS: {gdf.crs}")
            return gdf
        except Exception as e:
            print(f"Error reading GeoJSON: {e}")
            raise
    
    def merge_data_with_geography(self, 
                                geo_df: gpd.GeoDataFrame,
                                data_df: pd.DataFrame,
                                join_column: str) -> gpd.GeoDataFrame:
        """
        Merge statistical data with geographic features.
        
        Parameters:
        -----------
        geo_df : gpd.GeoDataFrame
            Geographic data
        data_df : pd.DataFrame
            Statistical data to merge
        join_column : str
            Column name to join on
            
        Returns:
        --------
        gpd.GeoDataFrame
            Merged geodataframe
        """
        return geo_df.merge(data_df, on=join_column, how='left')
    
    def simplify_geometries(self, 
                          gdf: gpd.GeoDataFrame, 
                          tolerance: float = 0.01) -> gpd.GeoDataFrame:
        """
        Simplify geometries for web display while preserving topology.
        
        Parameters:
        -----------
        gdf : gpd.GeoDataFrame
            Input geodataframe
        tolerance : float
            Simplification tolerance
            
        Returns:
        --------
        gpd.GeoDataFrame
            Simplified geodataframe
        """
        return gdf.copy().set_geometry(
            gdf.geometry.simplify(tolerance, preserve_topology=True)
        )
    
    def convert_to_web_mercator(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Convert to Web Mercator projection for web mapping."""
        return gdf.to_crs(epsg=3857)
    
    def export_for_dashboard(self, 
                           gdf: gpd.GeoDataFrame, 
                           filename: str,
                           simplify: bool = True) -> None:
        """
        Export GeoDataFrame to optimized GeoJSON for web dashboard.
        
        Parameters:
        -----------
        gdf : gpd.GeoDataFrame
            Input geodataframe
        filename : str
            Output filename
        simplify : bool
            Whether to simplify geometries
        """
        if simplify:
            gdf = self.simplify_geometries(gdf)
        
        output_path = self.data_dir / 'processed' / filename
        gdf.to_file(output_path, driver='GeoJSON')