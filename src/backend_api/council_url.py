import json
import os
from typing import Optional, Dict, Literal

from google import genai
from google.genai import types
from pydantic import BaseModel


class CouncilReportingInfo(BaseModel):
    """Pydantic model for council reporting page information."""

    url: str
    contact_number: Optional[str] = ""
    council_website: Optional[str] = ""
    confidence: Literal["high", "medium", "low"] = "medium"


def find_council_reporting_page(council_name: str) -> CouncilReportingInfo:
    """
    Find the fly-tipping reporting page for a UK council using Gemini with Google Search grounding.

    Args:
        council_name: Name of the UK council (e.g., "Greater London", "Westminster Council")

    Returns:
        CouncilReportingInfo model with fields:
            - url: The reporting page URL
            - contact_number: Council contact number (if found)
            - council_website: Main council website
            - confidence: How confident we are in the result ("high", "medium", "low")
    """
    result_text = ""
    try:
        # Get API key from environment
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Configure Gemini with Google Search grounding
        client = genai.Client(api_key=api_key)

        # Normalize council name
        council_search_name = council_name.replace(" Council", "").strip()

        # Create the prompt
        prompt = f"""Find the official fly-tipping reporting page for {council_search_name} Council in the UK.

I need you to find the SPECIFIC page where residents can report fly-tipping incidents, not just the main council website.

Please provide the following information in this EXACT JSON format (no markdown, no explanations, just valid JSON):

{{
  "url": "the direct URL to the fly-tipping reporting page or form",
  "contact_number": "council contact number for fly-tipping (format: 0xxx xxx xxxx or leave empty if not found)",
  "council_website": "main council website homepage",
  "confidence": "high/medium/low - how confident you are this is the correct reporting page"
}}

CRITICAL INSTRUCTIONS:
- You MUST find the ACTUAL reporting page, not just the homepage
- Look for pages with titles like "Report fly-tipping", "Report dumped rubbish", "Report environmental crime"
- The URL should be a .gov.uk or official council domain
- Only use official council sources
- If you cannot find a specific fly-tipping page, return the general environmental reporting page
- Return ONLY valid JSON, no markdown formatting, no code blocks
- If you're not confident, set confidence to "low" but still provide your best answer

Council to search: {council_search_name} Council, UK"""

        # Generate content with Google Search grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Part.from_text(text=prompt)],
            config=types.GenerateContentConfig(
                # Enable Google Search grounding for real-time web data
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.1,  # Lower temperature for more factual responses
            )
        )

        # Extract and clean the response
        result_text = response.text.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        # Parse JSON
        result = json.loads(result_text)

        # Validate required fields
        if "url" not in result or not result["url"]:
            raise ValueError("No URL found in response")

        # Ensure all fields exist
        result.setdefault("contact_number", "")
        result.setdefault("council_website", "")
        result.setdefault("confidence", "medium")

        info = CouncilReportingInfo(**result)

        print(f"✅ Found reporting page for {council_name}: {info.url}")
        return info

    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse JSON response: {e}")
        print(f"Raw response: {result_text}")
        # Return fallback
        return _get_fallback_result(council_name)

    except Exception as e:
        print(f"❌ Error finding council reporting page: {e}")
        # Return fallback
        return _get_fallback_result(council_name)


def _get_fallback_result(council_name: str) -> CouncilReportingInfo:
    """
    Generate a fallback result when the search fails.
    Uses a generic pattern based on council name.
    """
    council_slug = council_name.lower().replace(" council", "").replace(" ", "")

    # Common patterns for council websites
    possible_urls = [
        f"https://www.{council_slug}.gov.uk/report-fly-tipping",
        f"https://www.{council_slug}.gov.uk/report-it",
        f"https://www.{council_slug}.gov.uk/environment/fly-tipping",
    ]

    return CouncilReportingInfo(
        url=possible_urls[0],
        contact_number="0300 123 4567",  # Generic council number
        council_website=f"https://www.{council_slug}.gov.uk",
        confidence="low"
    )


# Batch function for efficiency
def find_multiple_councils_reporting_pages(council_names: list[str]) -> Dict[str, CouncilReportingInfo]:
    """
    Find reporting pages for multiple councils.
    Returns a dictionary mapping council name to their info.
    """
    results: Dict[str, CouncilReportingInfo] = {}

    for council_name in council_names:
        print(f"\n🔍 Searching for {council_name}...")
        try:
            results[council_name] = find_council_reporting_page(council_name)
        except Exception as e:
            print(f"⚠️ Failed for {council_name}: {e}")
            results[council_name] = _get_fallback_result(council_name)

    return results


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    # Test with a few councils
    test_councils = [
        "Hertfordshire County Council",
        "Three Rivers District Council",
    ]

    print("=" * 80)
    print("Testing Council Reporting Page Finder")
    print("=" * 80)

    for council in test_councils:
        print(f"\n{'=' * 80}")
        print(f"Council: {council}")
        print('=' * 80)

        result = find_council_reporting_page(council)

        print(f"\n📍 URL: {result.url}")
        print(f"📞 Contact: {result.contact_number}")
        print(f"🌐 Website: {result.council_website}")
        print(f"✓ Confidence: {result.confidence}")
        print()
