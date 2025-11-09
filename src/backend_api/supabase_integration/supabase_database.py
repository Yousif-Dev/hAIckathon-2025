import os
import pandas as pd
from supabase import create_client, Client
from typing import Optional


def load_IMDS(
        table_name: str = "haickathon-2025-postcodes-new",
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Load IMDS data from Supabase.
    Returns a pandas DataFrame with the same structure as the CSV file.

    Args:
        table_name: Name of the Supabase table 
        supabase_url: Supabase URL (optional, reads from env if not provided)
        supabase_key: Supabase key (optional, reads from env if not provided)

    Returns:
        pandas DataFrame with columns: postcode, council, constituency, rank, decile, country

    Raises:
        ValueError: If Supabase credentials are not provided or set in environment
        Exception: If data cannot be loaded from Supabase
    """
    try:
        # Get Supabase credentials
        url = supabase_url or os.environ.get("SUPABASE_URL")
        key = supabase_key or os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be provided or set in environment variables"
            )

        # Initialize Supabase client
        supabase: Client = create_client(url, key)

        # Fetch all data from the table
        response = supabase.table(table_name).select("*").execute()

        # Convert to DataFrame
        if not response.data:
            raise Exception(f"No data found in table '{table_name}'")

        df = pd.DataFrame(response.data)

        # Select only the columns we need (matching CSV structure)
        # This ensures compatibility even if table has extra columns like id, created_at, etc.
        required_columns = ['county', 'postcode', 'council', 'constituency', 'rank', 'decile', 'country']

        # Check if all required columns exist
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in table: {missing_columns}")

        # Return only the required columns in the correct order
        df = df[required_columns]

        # Ensure numeric columns are the correct type
        numeric_columns = ['rank']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"✅ Loaded {len(df)} counties from Supabase")
        return df

    except Exception as e:
        print(f"❌ Error loading county data from Supabase: {e}")
        raise

def load_county_data(
        table_name: str = "haickathon_2025_updated",
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Load county fly-tipping metrics from Supabase.
    Returns a pandas DataFrame with the same structure as the CSV file.

    This is a DROP-IN REPLACEMENT for:
        county_data = pd.read_csv("uk_county_flytip_metrics.csv")

    Just replace with:
        county_data = load_county_data()

    Args:
        table_name: Name of the Supabase table (default: "uk_county_flytip_metrics")
        supabase_url: Supabase URL (optional, reads from env if not provided)
        supabase_key: Supabase key (optional, reads from env if not provided)

    Returns:
        pandas DataFrame with columns: county, air_quality_impact, co2_emission_kg, quality_of_life_impact

    Raises:
        ValueError: If Supabase credentials are not provided or set in environment
        Exception: If data cannot be loaded from Supabase
    """
    try:
        # Get Supabase credentials
        url = supabase_url or os.environ.get("SUPABASE_URL")
        key = supabase_key or os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be provided or set in environment variables"
            )

        # Initialize Supabase client
        supabase: Client = create_client(url, key)

        # Fetch all data from the table
        response = supabase.table(table_name).select("*").execute()

        # Convert to DataFrame
        if not response.data:
            raise Exception(f"No data found in table '{table_name}'")

        df = pd.DataFrame(response.data)

        # Select only the columns we need (matching CSV structure)
        # This ensures compatibility even if table has extra columns like id, created_at, etc.
        required_columns = ['county', 'air_quality_impact', 'co2_emission_kg', 'quality_of_life_impact', 'deprivation_score', 'recycling_rate']

        # Check if all required columns exist
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in table: {missing_columns}")

        # Return only the required columns in the correct order
        df = df[required_columns]

        # Ensure numeric columns are the correct type
        numeric_columns = ['air_quality_impact', 'co2_emission_kg', 'quality_of_life_impact']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"✅ Loaded {len(df)} counties from Supabase")
        return df

    except Exception as e:
        print(f"❌ Error loading county data from Supabase: {e}")
        raise


def load_county_data_with_fallback(
        csv_path: str = "uk_county_flytip_metrics.csv",
        table_name: str = "haickathon_2025_table"
) -> pd.DataFrame:
    """
    Load county data with automatic fallback to CSV if Supabase fails.
    Useful during transition period.

    Args:
        csv_path: Path to CSV file (fallback)
        table_name: Supabase table name

    Returns:
        pandas DataFrame
    """
    try:
        # Try Supabase first
        return load_county_data(table_name=table_name)
    except Exception as e:
        print(f"⚠️ Supabase failed, falling back to CSV: {e}")
        try:
            return pd.read_csv(csv_path)
        except Exception as csv_error:
            print(f"❌ CSV fallback also failed: {csv_error}")
            raise


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    print("=" * 80)
    print("Testing Supabase County Data Loader")
    print("=" * 80)

    try:
        df = load_county_data()

        print(f"\n📊 Loaded Data:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")

        print(f"\n📋 First 5 rows:")
        print(df.head())

        print(f"\n📈 Data types:")
        print(df.dtypes)

        print(f"\n✅ Success! The function works exactly like pd.read_csv()")

        # Test that it works the same way as the CSV version
        print(f"\n🧪 Testing compatibility:")
        print(f"   Can filter: {len(df[df['county'] == 'Greater London'])} results")
        print(f"   Can compute mean: {df['co2_emission_kg'].mean():.2f}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nMake sure you:")
        print("1. Created the table in Supabase (see SUPABASE_MIGRATION_GUIDE.md)")
        print("2. Uploaded your CSV data to the table")
        print("3. Set SUPABASE_URL and SUPABASE_KEY in your .env file")
