import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from src.backend_api.classify_waste_bag_size import classify_waste_size_with_gemini
from src.backend_api.council_url import find_council_reporting_page
from src.backend_api.generate_summary import generate_summary
from src.backend_api.get_waste_type import get_waste_type
from src.backend_api.supabase.supabase_database import load_county_data
from src.backend_api.supabase.supabase_images import upload_image_to_supabase

app = FastAPI(title="Fly-Tipping Impact API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite default port
        "https://*.lovableproject.com",  # Lovable preview URLs
        "https://*.lovable.app",  # Lovable production URLs
        "*"  # Allow all origins (use cautiously!)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# In-memory storage for task results (in production, use Redis or a database)
task_results: Dict[str, dict] = {}

# Load county data
county_data = load_county_data()

# Postcode to county mapping (simplified - in production use a proper API/database)
POSTCODE_TO_COUNTY = {
    "SW": "Greater London",
    "SE": "Greater London",
    "E": "Greater London",
    "W": "Greater London",
    "N": "Greater London",
    "NW": "Greater London",
    "EC": "Greater London",
    "WC": "Greater London",
    "M": "Greater Manchester",
    "B": "West Midlands",
    "LS": "West Yorkshire",
    "L": "Merseyside",
    "S": "South Yorkshire",
    "NE": "Tyne and Wear",
    "BL": "Lancashire",
    "ME": "Kent",
    "CM": "Essex",
    "SO": "Hampshire",
    "GU": "Surrey",
    "WD": "Hertfordshire",
    "RG": "Berkshire",
    "HP": "Buckinghamshire",
    "OX": "Oxfordshire",
    "GL": "Gloucestershire",
    "SN": "Wiltshire",
    "BA": "Somerset",
    "EX": "Devon",
    "TR": "Cornwall",
    "BH": "Dorset",
    "BN": "East Sussex",
    "PO": "West Sussex",
    "NR": "Norfolk",
    "IP": "Suffolk",
    "CB": "Cambridgeshire",
    "LU": "Bedfordshire",
    "NN": "Northamptonshire",
    "LE": "Leicestershire",
    "NG": "Nottinghamshire",
    "DE": "Derbyshire",
    "ST": "Staffordshire",
    "SY": "Shropshire",
    "HR": "Herefordshire",
    "WR": "Worcestershire",
    "CV": "Warwickshire",
    "CH": "Cheshire",
    "CA": "Cumbria",
    "DH": "Durham",
    "NE": "Northumberland",
    "YO": "North Yorkshire",
    "HU": "East Riding of Yorkshire",
    "LN": "Lincolnshire",
    "LE": "Rutland",
    "PO": "Isle of Wight",
}

# Waste size multipliers
WASTE_SIZE_MULTIPLIERS = {
    "small_bag": 1.0,
    "medium_bag": 2.5,
    "large_bag": 5.0,
    "van": 15.0
}


# Pydantic Models
class EnvironmentalImpact(BaseModel):
    co2Emissions: float = Field(..., description="CO2 emissions in kg")
    wasteVolume: float = Field(..., description="Waste volume in tonnes")
    recyclingRate: float = Field(..., description="Recycling rate as percentage")


class CouncilInfo(BaseModel):
    name: str = Field(..., description="Council name")
    reportingUrl: str = Field(..., description="URL to report fly-tipping")
    contactNumber: str = Field(..., description="Council contact number")
    recommendations: List[str] = Field(..., description="List of recommendations")


class FlytippingImpactResponse(BaseModel):
    crimeChange: float = Field(..., description="Percentage change in crime rate")
    deprivationIndex: float = Field(..., description="Deprivation index on scale of 0-10")
    housePriceImpact: float = Field(..., description="Percentage impact on house prices")
    environmentalImpact: EnvironmentalImpact
    councilInfo: CouncilInfo
    summary: Optional[str] = Field(None, description="Summary of the impact")
    imageUrl: Optional[str] = Field(None, description="URL of the image, uploaded")


class SubmissionResponse(BaseModel):
    taskId: str = Field(..., description="Unique task identifier (GUID)")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class TaskStatusResponse(BaseModel):
    taskId: str
    status: str  # "pending", "processing", "completed", "failed"
    result: Optional[FlytippingImpactResponse] = None
    error: Optional[str] = None


def get_county_from_postcode(postcode: str) -> str:
    if not postcode or not isinstance(postcode, str):
        return "Greater London"

    # Normalize and split to get outward code (keep characters before the space)
    postcode = postcode.strip().upper()
    parts = postcode.split()
    outward = parts[0] if parts else postcode

    # Extract the leading letters from the outward code (postcode area)
    m = re.match(r"^([A-Z]+)", outward)
    area_letters = m.group(1) if m else ""

    # Try to find the longest matching prefix in the mapping
    for key in sorted(POSTCODE_TO_COUNTY.keys(), key=len, reverse=True):
        if outward.startswith(key) or area_letters.startswith(key):
            return POSTCODE_TO_COUNTY[key]

    # Default fallback
    return "Greater London"


def calculate_impact(county: str, waste_size: str, image_data: bytes) -> FlytippingImpactResponse:
    """Calculate the personalized impact metrics based on county and waste size."""

    # Get county metrics from CSV
    county_row = county_data[county_data['county'] == county]

    if county_row.empty:
        # Use average values if county not found
        county_row = county_data.mean(numeric_only=True)
        air_quality = county_row['air_quality_impact']
        co2_base = county_row['co2_emission_kg']
        qol_impact = county_row['quality_of_life_impact']
    else:
        air_quality = float(county_row['air_quality_impact'].values[0])
        co2_base = float(county_row['co2_emission_kg'].values[0])
        qol_impact = float(county_row['quality_of_life_impact'].values[0])

    # Apply waste size multiplier
    multiplier = WASTE_SIZE_MULTIPLIERS[waste_size]

    # Calculate impacts (using stub formulas)
    co2_emissions = co2_base * multiplier
    waste_volume_tonnes = 0.05 * multiplier  # Rough estimate: 50kg per "bag unit"

    # Crime change correlates with quality of life impact
    crime_change = qol_impact * 15.0 * multiplier  # Percentage increase

    # House price impact (negative correlation)
    house_price_impact = -qol_impact * 4.5 * multiplier

    # Deprivation index (higher fly-tipping = higher deprivation)
    deprivation_index = min(10.0, 5.0 + (qol_impact * 3.0))

    # Recycling rate (inversely related to fly-tipping)
    recycling_rate = max(10.0, 65.0 - (qol_impact * 50.0))

    # Waste type (household, construction, garden, hazardous)
    waste_type = get_waste_type(image_data)

    # Summary
    # Use AI to generate summary here
    summary = generate_summary(county, waste_size, crime_change, house_price_impact, co2_emissions, waste_type)

    image_url = upload_image_to_supabase(image_data)  # Stub function to upload image

    # Council info (stub data)
    council_recommendations = [
        "Report fly-tipping incidents immediately via the council website",
        "Use licensed waste carriers - check the Environment Agency register",
        "Take bulky waste to your local household recycling centre",
        "Consider using the council's bulky waste collection service",
        f"Fly-tipping costs your council £{int(multiplier * 200)} to clear - help us reduce this burden"
    ]

    council_url_llm = find_council_reporting_page(county)

    return FlytippingImpactResponse(
        crimeChange=round(crime_change, 1),
        summary=summary,
        imageUrl=image_url,
        deprivationIndex=round(deprivation_index, 1),
        housePriceImpact=round(house_price_impact, 1),
        environmentalImpact=EnvironmentalImpact(
            co2Emissions=round(co2_emissions, 1),
            wasteVolume=round(waste_volume_tonnes, 2),
            recyclingRate=round(recycling_rate, 1)
        ),
        councilInfo=CouncilInfo(
            name=f"{county} Council",
            reportingUrl=council_url_llm.council_website,
            contactNumber=council_url_llm.contact_number,
            recommendations=council_recommendations
        )
    )


async def process_flytipping_analysis(task_id: str, postcode: str, image_data: bytes):
    """Background task to process fly-tipping analysis."""
    try:
        # Update status to processing
        task_results[task_id]["status"] = "processing"

        # Step 1: Get county from postcode
        county = get_county_from_postcode(postcode)

        # Step 2: Classify waste size using OpenAI (stubbed)
        waste_size = classify_waste_size_with_gemini(image_data)

        # Step 3: Calculate impact metrics
        impact_result = calculate_impact(county, waste_size, image_data)

        # Store result
        task_results[task_id]["status"] = "completed"
        task_results[task_id]["result"] = impact_result.model_dump()
        task_results[task_id]["metadata"] = {
            "county": county,
            "waste_size": waste_size,
            "processed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        task_results[task_id]["status"] = "failed"
        task_results[task_id]["error"] = str(e)


@app.post("/api/submit", response_model=SubmissionResponse)
async def submit_flytipping_report(
        postcode: str,
        image: UploadFile = File(...),
        background_tasks: BackgroundTasks = None
):
    """
    Submit a fly-tipping report with postcode and image.
    Returns a task ID for checking results.
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())

    # Read image data
    image_data = await image.read()

    # Initialize task in storage
    task_results[task_id] = {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "postcode": postcode,
    }

    # Add background task
    background_tasks.add_task(
        process_flytipping_analysis,
        task_id,
        postcode,
        image_data
    )

    return SubmissionResponse(
        taskId=task_id,
        status="pending",
        message="Your fly-tipping report has been submitted and is being processed."
    )


@app.get("/api/result/{task_id}", response_model=TaskStatusResponse)
async def get_analysis_result(task_id: str):
    """
    Get the analysis result for a submitted fly-tipping report.
    Returns the impact metrics once processing is complete.
    """
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task_data = task_results[task_id]
    status = task_data["status"]

    response = TaskStatusResponse(
        taskId=task_id,
        status=status
    )

    if status == "completed":
        response.result = FlytippingImpactResponse(**task_data["result"])
    elif status == "failed":
        response.error = task_data.get("error", "Unknown error occurred")

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "counties_loaded": len(county_data)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
