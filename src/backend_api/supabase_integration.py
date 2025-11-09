import os
from datetime import datetime
from supabase import create_client, Client
from typing import Optional
import uuid


def upload_image_to_supabase(
        image_data: bytes,
        filename: Optional[str] = None,
        bucket_name: str = "flytipping-images"
) -> str:
    """
    Upload an image to Supabase Storage and return the public URL.

    Args:
        image_data: Raw image bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        bucket_name: Name of the Supabase storage bucket (default: "flytipping-images")

    Returns:
        Public URL of the uploaded image

    Raises:
        ValueError: If Supabase credentials are not set
        Exception: If upload fails
    """
    try:
        # Get Supabase credentials from environment
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")  # This should be your service_role key or anon key

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "Get these from your Supabase project settings."
            )

        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"flytipping_{timestamp}_{unique_id}.jpg"

        # Ensure filename has extension
        if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            filename += '.jpg'

        # Upload to Supabase Storage
        # Path structure: bucket_name/YYYY-MM/filename for better organization
        year_month = datetime.utcnow().strftime("%Y-%m")
        storage_path = f"{year_month}/{filename}"

        response = supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=image_data,
            file_options={
                "content-type": "image/jpeg",
                "cache-control": "3600",
                "upsert": "false"  # Don't overwrite if exists
            }
        )

        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)

        print(f"✅ Image uploaded successfully to: {public_url}")
        return public_url

    except Exception as e:
        print(f"❌ Error uploading image to Supabase: {e}")
        raise


def create_storage_bucket_if_not_exists(bucket_name: str = "flytipping-images") -> bool:
    """
    Helper function to create the storage bucket if it doesn't exist.
    Call this once during setup/initialization.

    Args:
        bucket_name: Name of the bucket to create

    Returns:
        True if bucket was created or already exists
    """
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        supabase: Client = create_client(supabase_url, supabase_key)

        # Try to create bucket (will fail if already exists, which is fine)
        try:
            supabase.storage.create_bucket(
                bucket_name,
                options={
                    "public": True,  # Make bucket public so images are accessible
                    "file_size_limit": 5242880,  # 5MB limit
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"]
                }
            )
            print(f"✅ Storage bucket '{bucket_name}' created successfully")
            return True
        except Exception as bucket_error:
            # Bucket might already exist
            if "already exists" in str(bucket_error).lower():
                print(f"ℹ️ Storage bucket '{bucket_name}' already exists")
                return True
            else:
                raise bucket_error

    except Exception as e:
        print(f"❌ Error creating storage bucket: {e}")
        return False


if __name__ == "__main__":
    # Test the function
    from dotenv import load_dotenv

    load_dotenv()

    # First, create the bucket (run this once)
    print("Step 1: Creating storage bucket...")
    create_storage_bucket_if_not_exists()

    # Then test upload
    print("\nStep 2: Testing image upload...")
    test_image_path = r"C:\Users\yousi\Downloads\small_bag_example_fly.png"

    try:
        with open(test_image_path, "rb") as img_file:
            image_bytes = img_file.read()
            public_url = upload_image_to_supabase(image_bytes)
            print(f"\n🎉 Success! Image available at:\n{public_url}")
    except FileNotFoundError:
        print(f"\n⚠️ Test image not found at: {test_image_path}")
        print("Update the path to test the function")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")