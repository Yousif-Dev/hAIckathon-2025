import googlemaps
from typing import List, Tuple
import json
import os

# Initialize the Google Maps client
# Make sure to set your API key as an environment variable or replace it here
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
DEFAULT_DISTANCE=150

API_TYPE_TO_CATEGORY = {
    "apartment_building": "residentialAreas",
    "apartment_complex": "residentialAreas",
    "condominium_complex": "residentialAreas",
    "housing_complex": "residentialAreas",
    "neighborhood": "residentialAreas",
    "place_of_worship": "placeOfWorship",
    "church": "placeOfWorship",
    "hindu_temple": "placeOfWorship",
    "mosque": "placeOfWorship",
    "synagogue": "placeOfWorship",
    "preschool": "schoolsAndEducationalFacilities",
    "primary_school": "schoolsAndEducationalFacilities",
    "school": "schoolsAndEducationalFacilities",
    "secondary_school": "schoolsAndEducationalFacilities",
    "hospital": "healthcareFacilities",
    "doctor": "healthcareFacilities",
    "dentist": "healthcareFacilities",
    "dental_clinic": "healthcareFacilities",
    "pharmacy": "healthcareFacilities",
    "medical_lab": "healthcareFacilities",
    "physiotherapist": "healthcareFacilities",
    "chiropractor": "healthcareFacilities",
    "park": "parksAndRecreationAreas",
    "national_park": "parksAndRecreationAreas",
    "state_park": "parksAndRecreationAreas",
    "garden": "parksAndRecreationAreas",
    "botanical_garden": "parksAndRecreationAreas",
    "picnic_ground": "parksAndRecreationAreas",
    "beach": "waterwaysAndWetlands",
    "farm": "agriculturalLand",
    "ranch": "agriculturalLand",
    "wildlife_refuge": "natureReservesAndProtectedHabitats",
    "wildlife_park": "natureReservesAndProtectedHabitats",
    "corporate_office": "corporateOffice",
    "playground": "playgroundsAndRecreationalFacilitiesForChildren",
    "childrens_camp": "playgroundsAndRecreationalFacilitiesForChildren",
    "dog_park": "playgroundsAndRecreationalFacilitiesForChildren",
}

def postcode_to_coordinates(postcode: str) -> Tuple[float, float]:
    """
    Convert a postcode to latitude and longitude coordinates.
    
    Args:
        postcode: The postcode to convert (e.g., "SW1A 1AA" for UK)
    
    Returns:
        Tuple of (latitude, longitude)
    
    Raises:
        ValueError: If the postcode cannot be geocoded
    """
    try:
        geocode_result = gmaps.geocode(address=postcode)
        if not geocode_result:
            raise ValueError(f"Could not find coordinates for postcode: {postcode}")
        
        location = geocode_result[0]["geometry"]["location"]
        return location["lat"], location["lng"]
    except Exception as e:
        raise ValueError(f"Error geocoding postcode {postcode}: {str(e)}")


def get_nearby_place_types(latitude: float, longitude: float, radius: int = DEFAULT_DISTANCE, debug=False) -> List[str]:
    """
    Find nearby place types at a given location.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius: Search radius in meters (default: DEFAULT_DISTANCE)
    
    Returns:
        List of place type categories found nearby
    """
    found_types = set()
    
    places_result = gmaps.places_nearby(
        location=(latitude, longitude),
        radius=radius,
    )

    type_set = set()
    for result in places_result.get('results',[]):
        type_set.update(result.get('types'))

    if debug:
        print(type_set)
        print(", ".join([x.get('name') for x in places_result.get('results')]))
    for place_type in API_TYPE_TO_CATEGORY:
        try:
            # check if the type is in the api response and add it
            if place_type in type_set:
                found_types.add(API_TYPE_TO_CATEGORY[place_type])
        except Exception as e:
            print(f"Warning: Error searching for {place_type}: {str(e)}")
            continue
    result = sorted(list(found_types))
    if debug:
        print(type_set)
        print(result)
    return result


def find_places_by_postcode(postcode: str, radius: int = DEFAULT_DISTANCE, debug=False) -> Tuple[Tuple[float, float], List[str]]:
    """
    Convenience function that combines postcode lookup and nearby place type search.
    
    Args:
        postcode: The postcode to search around
        radius: Search radius in meters (default: DEFAULT_DISTANCE)
    
    Returns:
        Tuple of (coordinates, place_types) where coordinates is (lat, lng) and place_types is a list of strings
    """
    coords = postcode_to_coordinates(postcode)
    place_types = get_nearby_place_types(coords[0], coords[1], radius, debug)
    return coords, place_types


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    import sys

    load_dotenv()
    try:
        postcode = f"{sys.argv[1]}"  # Replace with your postcode
        coords, types = find_places_by_postcode(postcode,debug=True)
        
        print(f"Postcode: {postcode}")
        print(f"Coordinates: {coords[0]}, {coords[1]}")
        print(f"Nearby place types found:")
        for place_type in types:
            print(f"  - {place_type}")
    except ValueError as e:
        print(f"Error: {e}")
