import os

from google import genai
from google.genai import types


def get_waste_type(image_data: bytes) -> str:
    """
    Classify waste type using Google Gemini Vision API.
    Returns one of: household, construction, garden, hazardous, furniture, electrical

    Args:
        image_data: Raw image bytes

    Returns:
        A string indicating the waste type category
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Configure Gemini
        client = genai.Client(api_key=api_key)

        # Create the prompt
        prompt = """You are an expert at analyzing fly-tipping (illegal waste dumping) incidents.

Analyze this image and classify the TYPE of waste into EXACTLY ONE of these categories:

1. household - General household rubbish, black bags, food waste, general trash
2. construction - Building materials, rubble, timber, plasterboard, bricks, cement
3. garden - Grass cuttings, branches, leaves, soil, garden waste
4. hazardous - Paint, chemicals, asbestos, batteries, oil, toxic materials
5. furniture - Sofas, mattresses, chairs, tables, wardrobes, cabinets
6. electrical - White goods (fridges, washers), TVs, computers, electronic items

CRITICAL INSTRUCTIONS:
- You MUST respond with ONLY ONE of these exact words: household, construction, garden, hazardous, furniture, electrical
- Do NOT include any other text, explanation, or punctuation
- If you see multiple types, choose the DOMINANT or most visible type
- If you cannot clearly identify the waste, respond with: household
- Base your decision on what is MOST visible in the image

Your response (one word only):"""

        # Generate content with image
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
            ]
        )

        # Extract and clean the response
        classification = response.text.strip().lower()

        # Validate the response
        valid_types = ["household", "construction", "garden", "hazardous", "furniture", "electrical"]

        if classification in valid_types:
            return classification
        else:
            # If Gemini returns something unexpected, try to parse it
            for waste_type in valid_types:
                if waste_type in classification:
                    return waste_type

            # Default fallback if we can't parse
            print(f"Warning: Unexpected Gemini response for waste type: {classification}")
            return "household"

    except Exception as e:
        print(f"Error calling Gemini API for waste type: {e}")
        # Fallback to household on error
        return "household"


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    test_image_path = r"C:\Users\yousi\Downloads\small_bag_example_fly.png"

    try:
        with open(test_image_path, "rb") as img_file:
            image_bytes = img_file.read()
            waste_classification = get_waste_type(image_bytes)
            print(f"Classified waste type: {waste_classification}")
    except FileNotFoundError:
        print(f"Test image not found at: {test_image_path}")
        print("Update the path to test the function")