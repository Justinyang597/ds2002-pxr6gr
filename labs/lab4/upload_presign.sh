#!/bin/bash
# This script uploads a file to an S3 bucket and then generates a presigned URL.
# Usage: ./upload_presign.sh <local-file> <bucket-name> <expiration-in-seconds>


if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <local-file> <bucket-name> <expiration-in-seconds>"
  exit 1
fi

LOCAL_FILE="$1"
BUCKET_NAME="$2"
EXPIRATION="$3"
FILE_NAME=$(basename "$LOCAL_FILE")

# Upload the file to the specified S3 bucket.
echo "Uploading $LOCAL_FILE to s3://$BUCKET_NAME/$FILE_NAME ..."
aws s3 cp "$LOCAL_FILE" s3://"$BUCKET_NAME"/"$FILE_NAME"
if [ $? -ne 0 ]; then
  echo "Error: File upload failed."
  exit 1
fi

# Generate a presigned URL with the given expiration.
echo "Generating presigned URL for s3://$BUCKET_NAME/$FILE_NAME ..."
PRESIGNED_URL=$(aws s3 presign s3://"$BUCKET_NAME"/"$FILE_NAME" --expires-in "$EXPIRATION")
if [ $? -ne 0 ]; then
  echo "Error: Presigning URL failed."
  exit 1
fi

echo "File uploaded successfully!"
echo "Presigned URL (expires in $EXPIRATION seconds):"
echo "$PRESIGNED_URL"
