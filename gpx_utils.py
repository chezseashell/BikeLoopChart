import gpxpy
import numpy as np
from scipy.spatial import cKDTree

def load_gpx(filename):
    """Load GPX file and extract latitude, longitude, elevation, and distances."""
    with open(filename, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    lats, lons, elevations, distances = [], [], [], []
    distance = 0  # Cumulative distance
    prev_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lats.append(point.latitude)
                lons.append(point.longitude)
                elevations.append(point.elevation)

                if prev_point:
                    delta_dist = np.sqrt((point.latitude - prev_point.latitude) ** 2 + (point.longitude - prev_point.longitude) ** 2)
                    distance += delta_dist * 111  # Convert degrees to km

                distances.append(distance)
                prev_point = point

    return lats, lons, elevations, distances

def build_track_tree(lats, lons):
    """Create a k-d tree for quick nearest neighbor searches."""
    track_coords = np.column_stack((lats, lons))
    return cKDTree(track_coords)

def match_to_nearest_point(df, track_tree, distances):
    """Find the nearest GPX track point for each POI or restroom."""
    return [distances[track_tree.query([row["Latitude"], row["Longitude"]])[1]] for _, row in df.iterrows()]
