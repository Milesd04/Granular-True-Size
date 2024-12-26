import json
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely import unary_union

# TAKES GEOJSONS AND PROCESSES THEM INTO A FORMAT COMPATIBLE WITH LEAFLET TRUESIZE

def simplify_geometry(geometry: BaseGeometry, tolerance: float) -> BaseGeometry:
    """
    Simplify a geometry with the specified tolerance.
    """
    return geometry.simplify(tolerance, preserve_topology=True)


def convert_to_multipolygon(geometry):
    """
    Convert a geometry to MultiPolygon if it isn't already.
    """
    if isinstance(geometry, Polygon):
        return MultiPolygon([geometry])

    if isinstance(geometry, MultiPolygon):
        return geometry

    raise ValueError(f"Geometry type {type(geometry)} not supported")


def merge_polygons(input_geojson: dict) -> dict:
    """
    Merge all polygons in the GeoJSON into a single polygon if multiple are present,
    preserving interior rings (holes).
    """
    geometries = [
        shape(feature["geometry"]) for feature in input_geojson.get("features", [])
    ]
    merged_geometry = unary_union(geometries)

    merged_geometry = convert_to_multipolygon(merged_geometry)
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": merged_geometry, "properties": {}}
        ],
    }


def transform_multipolygon_coordinates(coordinates):
    """
    Transforms MultiPolygon coordinates to the correct nesting structure,
    preserving both exterior and interior rings.
    """
    transformed_polygons = []
    for polygon in coordinates:
        # polygon is a list where first element is exterior ring and rest are interior rings
        transformed_polygons.extend(polygon)

    # Wrap all rings in a single outer array
    return [transformed_polygons]


def transform_features(geojson_data: dict) -> str:
    """
    Transform GeoJSON features into a simplified format with correct MultiPolygon structure.
    """
    transformed_features_lst = []

    for feature in geojson_data.get("features", []):

        geometry = shape(feature["geometry"])
        multipolygon = convert_to_multipolygon(geometry)

        coordinates = mapping(multipolygon)["coordinates"]
        coordinates = transform_multipolygon_coordinates(coordinates)

        transformed_feature = {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "MultiPolygon", "coordinates": coordinates},
        }
        transformed_features_lst.append(transformed_feature)

    return "\n".join(json.dumps(feature, indent=2) for feature in transformed_features_lst)


def process_geojson(input_geojson: dict, tolerance: float) -> dict:
    """
    Simplifies the geometries in a GeoJSON object and formats the output.
    """
    if len(input_geojson.get("features", [])) > 1:
        input_geojson = merge_polygons(input_geojson)

    # simplify geometries
    simplified_features = []
    for feature in input_geojson.get("features", []):
        geometry = shape(feature["geometry"])
        simplified_geometry = simplify_geometry(geometry, tolerance)

        # Ensure simplified geometry is MultiPolygon
        simplified_geometry = convert_to_multipolygon(simplified_geometry)
        feature_id = feature.get("id", "UNKNOWN")
        feature_properties = feature.get("properties", {})

        simplified_features.append(
            {
                "type": "Feature",
                "id": feature_id,
                "properties": feature_properties,
                "geometry": simplified_geometry,
            }
        )

    return {"type": "FeatureCollection", "features": simplified_features}


def simplify_and_transform_geojson(
    input_path: str, intermediate_path: str, tolerance: float
):
    """
    Complete pipeline to simplify and transform GeoJSON data.
    """
    with open(input_path, "r") as f:
        geojson_data = json.load(f)

    simplified_geojson = process_geojson(geojson_data, tolerance)

    transformed_geojson = transform_features(simplified_geojson)

    with open(intermediate_path, "w") as f:
        f.write(transformed_geojson)
    print(f"Transformed GeoJSON written to {intermediate_path}")


if __name__ == "__main__":
    INPUT_GEOJSON = r"data\raw\Japan\Tokyo_Prefecture.geojson"
    OUTPUT_GEOJSON = r"data\Tokyo Prefecture.geojson"
    SIMPLIFICATION_TOLERANCE = 0.0001

    simplify_and_transform_geojson(INPUT_GEOJSON, OUTPUT_GEOJSON, SIMPLIFICATION_TOLERANCE)
