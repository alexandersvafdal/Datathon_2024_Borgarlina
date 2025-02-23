from typing import List, Dict, Tuple
from shapely.geometry import Point, shape
from shapely.validation import make_valid
from shapely import Polygon
from data_processing.get_smallAreaInfo import get_smallAreas


def get_station_coverage(
    small_areas: List[Dict], station_coords: Tuple[float, float], radius_meters: float
) -> List[Dict]:
    """
    Identify small areas within a given range of a station and calculate coverage percentage.

    Args:
        small_areas (List[Dict]): List of small area geometries as lists of coordinates.
        station_coords (Tuple[float, float]): Coordinates of the station (x, y) in meters (EPSG:3057).
        radius_meters (float): The range to check (e.g., 400 meters).

    Returns:
        List[Dict]: A list of small area features with the percentage of the ring they cover.
    """
    # Create a buffer (ring) around the station
    station_point = Point(station_coords)
    station_buffer = station_point.buffer(radius_meters)

    # Total buffer area
    buffer_area = station_buffer.area

    # Find small areas that intersect with the buffer
    covered_areas = []
    for area in small_areas:
        # Convert the list of tuples to a proper Polygon structure
        coordinates = area["geometry"]
        geometry = Polygon(coordinates)

        # Validate and fix invalid geometries
        if not geometry.is_valid:
            # print(f"Invalid geometry detected for Area ID: {area['id']}. Attempting to fix.")
            geometry = make_valid(geometry)

        # Simplify geometry to avoid potential issues with highly complex polygons
        geometry = geometry.simplify(tolerance=0.01, preserve_topology=True)

        # Check intersection with the station buffer
        if geometry.intersects(station_buffer):
            # Calculate intersection area
            intersection = geometry.intersection(station_buffer)
            intersection_area = intersection.area

            # Calculate the percentage of the radius covered by this area
            coverage_percentage = (intersection_area / buffer_area) * 100

            # Calculate the percentage of the area covered by the radius
            small_zone_percentage = (intersection_area / geometry.area) * 100

            # Add the area and coverage percentage to the result
            covered_areas.append({
                "id": area["id"],  # Include the area's ID or relevant metadata
                "coverage_percentage": coverage_percentage,
                "small_zone_percentage": small_zone_percentage
            })

    return covered_areas

if __name__ == '__main__':
    # Example station location and radius
    station_coords = (356250.0, 408250.0)  # EPSG:3057 coordinates
    radius_meters = 400  # 400 meters

    # Get small areas
    covered_areas = get_station_coverage(get_smallAreas(), station_coords, radius_meters)

    # Print results
    for area in covered_areas:
        print(f"Area ID: {area['id']}, Coverage: {area['coverage_percentage']:.2f}%")
