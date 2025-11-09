import os
from google import genai
from google.genai import types


def generate_summary(
        county: str,
        waste_size: str,
        crime_change: float,
        house_price_impact: float,
        co2_emissions: float,
        waste_type: str
) -> str:
    """
    Generate a personalized one-paragraph summary using Google Gemini.
    Creates a narrative about how this fly-tipping incident affects the individual.

    Args:
        county: The county where the incident occurred
        waste_size: Size classification (small_bag, medium_bag, large_bag, van)
        crime_change: Percentage change in crime rate
        house_price_impact: Percentage impact on house prices (negative)
        co2_emissions: CO2 emissions in kg
        waste_type: Type of waste (household, construction, garden, hazardous)

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

Generate a compelling, personalized one-paragraph summary (4-6 sentences) that tells a story about how this fly-tipping incident impacts the individual resident.

INCIDENT DETAILS:
- Location: {county}
- Waste size: {waste_size.replace('_', ' ')}
- Waste type: {waste_type}
- Crime increase in area: {crime_change:.1f}%
- House price impact: {house_price_impact:.1f}%
- CO2 emissions: {co2_emissions:.1f} kg

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
            f"It contributes to a {abs(house_price_impact):.1f}% reduction in local property values, "
            f"releases {co2_emissions:.1f}kg of CO2 into your air, and is associated with a "
            f"{crime_change:.1f}% increase in local crime rates. Every unreported incident makes "
            f"your neighborhood less safe and less valuable. By reporting this, you're taking "
            f"the first step toward breaking the cycle and reclaiming your community's future."
        )


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    test_summary = generate_summary(
        county="Greater London",
        waste_size="medium_bag",
        crime_change=12.5,
        house_price_impact=-3.2,
        co2_emissions=45.8,
        waste_type="hazardous"
    )

    print("Generated Summary:")
    print("-" * 80)
    print(test_summary)
    print("-" * 80)