import os
from google import genai
from google.genai import types

def generate_summary(
        county: str,
        waste_size: str,
        waste_type: str,
        area_features: list[str]
) -> str:
    """
    Generate a personalized one-paragraph summary using Google Gemini.
    Creates a narrative about how this fly-tipping incident affects the individual.

    Args:
        county: The county where the incident occurred
        waste_size: Size classification (small_bag, medium_bag, large_bag, van)
        waste_type: Type of waste (household, construction, garden, hazardous)
        area_features: list of nearby features, e.g ["schoolsAndEducationalFacilities", "residentialAreas", "placeOfWorship"]

    Returns:
        A personalized one-paragraph summary string
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Configure Gemini
        client = genai.Client(api_key=api_key)

        # Create the prompt
        prompt = f"""You are a community impact analyst helping residents understand how fly-tipping affects them personally.

Generate a compelling, personalized one-paragraph summary (4-6 sentences) that tells a story about how this fly-tipping incident impacts local residents.

INCIDENT DETAILS:
- Location: {county}
- Waste size: {waste_size.replace('_', ' ')}
- Waste type: {waste_type}
- Nearby features which should be mentioned: {", ".join(area_features)}

WRITING GUIDELINES:
1. Start with immediate personal impact (their property value, their safety, their environment)
2. Make it feel personal and direct - use "your" and focus on tangible effects
3. Connect the dots between this incident and their daily life
4. Include a forward-looking element about community action
5. Keep it conversational but impactful - avoid jargon
6. DO NOT use bullet points or lists - write flowing prose
7. End on a note that empowers action
8. Do not have it be overly dramatic, but still personable.

TONE: Concerned but constructive, factual but engaging, personal but not preachy

Your one-paragraph summary:"""

        # Generate content
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Part.from_text(text=prompt)]
        )

        # Extract and clean the response
        summary = response.text.strip()

        # Remove any markdown formatting that might have crept in
        summary = summary.replace("**", "").replace("*", "")

        return summary

    except Exception as e:
        print(f"Error calling Gemini API for summary: {e}")

        # Fallback summary if API fails
        return (
            f"This {waste_type} fly-tipping incident in {county} directly impacts your quality of life. "
        )


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    test_summary = generate_summary(
        county="Greater London",
        waste_size="medium_bag",
        waste_type="hazardous",
        area_features=["residentialAreas", "placeOfWorship"]
    )

    print("Generated Summary:")
    print("-" * 80)
    print(test_summary)
    print("-" * 80)
