Based on the code, here's the API schema for your flytipping application:
📋 API Endpoints
1. POST /api/report

Submit a flytipping report with an image and location.

Input (Request):

    Method: POST
    Content-Type: multipart/form-data
    Body:

    FormData with:
    - image: File (image file)
    - location: string (street address or postcode)

Output (Response):

    Status: 200 OK
    Content-Type: application/json
    Body: Any JSON object (currently not strictly defined - the app just passes it through to the Impact page via navigation state)

2. GET /api/impact

Retrieve impact analysis data for a specific location.

Input (Request):

    Method: GET
    Query Parameters:
        location: string (URL-encoded location)
    Example: /api/impact?location=SW1A%201AA

Output (Response):

    Status: 200 OK
    Content-Type: application/json
    Body:

    {
      crimeChange: number,              // e.g., 12.5 (represents +12.5%)
      deprivationIndex: number,         // e.g., 6.8 (scale of 0-10)
      housePriceImpact: number,         // e.g., -3.2 (represents -3.2%)
      environmentalImpact: {
        co2Emissions: number,           // e.g., 450 (in kg)
        wasteVolume: number,            // e.g., 2.3 (in tonnes)
        recyclingRate: number           // e.g., 18 (represents 18%)
      },
      councilInfo: {
        name: string,                   // e.g., "Westminster City Council"
        reportingUrl: string,           // e.g., "https://council.gov.uk/report"
        contactNumber: string,          // e.g., "0800 123 4567"
        recommendations: string[]       // Array of recommendation strings
      }
    }

Example Response:

{
  "crimeChange": 12.5,
  "deprivationIndex": 6.8,
  "housePriceImpact": -3.2,
  "environmentalImpact": {
    "co2Emissions": 450,
    "wasteVolume": 2.3,
    "recyclingRate": 18
  },
  "councilInfo": {
    "name": "Westminster City Council",
    "reportingUrl": "https://westminster.gov.uk/report-flytipping",
    "contactNumber": "0800 123 4567",
    "recommendations": [
      "Report the incident to the council immediately",
      "Do not touch or move any waste materials",
      "Take photographs from multiple angles if safe to do so",
      "Note any vehicle details if witnessed",
      "Keep a record of your report reference number"
    ]
  }
}

📝 Notes

    Currently, the app uses localhost:8080 as the API base URL
    The /api/report endpoint response structure is flexible (not strictly validated)
    If the /api/impact endpoint fails, the app falls back to mock data
    The location parameter in the GET request is URL-encoded using encodeURIComponent()

Would you like me to create a plan to replace these localhost API calls with real Lovable Cloud backend functionality using edge functions and storage?
