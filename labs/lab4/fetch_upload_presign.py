#!/usr/bin/env python3
import argparse
import os
import requests
import boto3

def main():
    parser = argparse.ArgumentParser(
        description="Fetch a file from the internet, upload to S3, and generate a presigned URL."
    )
    parser.add_argument("url", help="The URL of the file to fetch")
    parser.add_argument("bucket", help="The name of the S3 bucket to upload to")
    parser.add_argument("object_key", help="The S3 object key (destination filename/path in the bucket)")
    parser.add_argument(
        "-e", "--expires", type=int, default=604800,
        help="Expiration time (in seconds) for the presigned URL (default: 604800 seconds, 7 days)"
    )
    args = parser.parse_args()

    # Fetch the file from the internet
    print(f"Fetching file from {args.url}...")
    response = requests.get(args.url)
    if response.status_code != 200:
        print(f"Failed to fetch file. HTTP status code: {response.status_code}")
        return

    # Save the fetched content locally
    local_filename = os.path.basename(args.object_key)
    print(f"Saving file locally as {local_filename}...")
    try:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error saving file: {e}")
        return

    # Upload the file to S3 (kept private by default)
    print(f"Uploading {local_filename} to bucket '{args.bucket}' with key '{args.object_key}'...")
    s3 = boto3.client('s3', region_name='us-east-1')
    try:
        s3.upload_file(local_filename, args.bucket, args.object_key)
    except Exception as e:
        print(f"Error during file upload: {e}")
        return

    # Generate a presigned URL for the uploaded file
    print("Generating presigned URL...")
    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': args.bucket, 'Key': args.object_key},
            ExpiresIn=args.expires
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return

    # Output the presigned URL
    print(f"Presigned URL (expires in {args.expires} seconds):")
    print(presigned_url)

    # Clean up: remove the local file if desired
    try:
        os.remove(local_filename)
        print("Temporary local file removed.")
    except Exception as e:
        print(f"Warning: Could not remove local file: {e}")

if __name__ == "__main__":
    main()
