import base64
import os

from google import genai
from google.genai import types


def classify_waste_size_with_gemini(image_data: bytes) -> str:
    """
    Classify waste size using Google Gemini Vision API.
    Returns one of: small_bag, medium_bag, large_bag, van
    """
    try:
        # Get API key from environment
        api_key = os.environ["GEMINI_API_KEY"]
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Configure Gemini
        client = genai.Client(api_key=api_key)

        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Create the prompt
        prompt = """You are an expert at analyzing fly-tipping (illegal waste dumping) incidents.

Analyze this image and classify the amount of waste into EXACTLY ONE of these four categories:

1. small_bag - A single small refuse bag or equivalent (roughly one shopping bag worth)
2. medium_bag - 2-3 bags or a medium-sized pile (roughly a wheelie bin worth)
3. large_bag - Multiple bags or a large pile (roughly 4-8 bags worth)
4. van - A van-sized load or larger (clearly would require a vehicle to transport)

CRITICAL INSTRUCTIONS:
- You MUST respond with ONLY ONE of these exact words: small_bag, medium_bag, large_bag, van
- Do NOT include any other text, explanation, or punctuation
- If you cannot see waste in the image, respond with: small_bag
- Base your decision on the VOLUME of waste visible

Your response (one word only):"""

        # Prepare the image for Gemini
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_base64
            }
        ]

        # Generate content
        response = client.models.generate_content(model="gemini-2.5-flash",
                                                  contents=[
                                                      types.Part.from_text(text=prompt),
                                                      types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
                                                  ]
                                                  )

        # Extract and clean the response
        classification = response.text.strip().lower()

        # Validate the response
        valid_sizes = ["small_bag", "medium_bag", "large_bag", "van"]

        if classification in valid_sizes:
            return classification
        else:
            # If Gemini returns something unexpected, try to parse it
            for size in valid_sizes:
                if size in classification:
                    return size

            # Default fallback if we can't parse
            print(f"Warning: Unexpected Gemini response: {classification}")
            return "medium_bag"

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback to medium_bag on error
        return "medium_bag"


if __name__ == "__main__":
    # Test the function with a sample image
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
    test_image_path = r"C:\Users\yousi\Downloads\small_bag_example_fly.png"
    with open(test_image_path, "rb") as img_file:
        image_bytes = img_file.read()
        size_classification = classify_waste_size_with_gemini(image_bytes)
        print(f"Classified waste size: {size_classification}")
