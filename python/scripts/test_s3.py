#!/usr/bin/env python

import os
import subprocess

# MinIO and S3fs configurations
minio_url = 'https://ace-minio-1.loris.ca:9000'  # MinIO endpoint
access_key = 'lorisadmin-ro'        # Replace with MinIO access key
secret_key = 'Tn=qP3LupmXnMuc'   # Replace with MinIO secret key
bucket_name = 'loris-rb-data'    # Replace with your bucket name
mount_point = '/data/test_s3'    # Local directory where bucket will be mounted

# Step 1: Create mount point directory if it doesn't exist
if not os.path.exists(mount_point):
    os.makedirs(mount_point)
    print(f"Mount point directory '{mount_point}' created.")

# Step 2: Create credentials file for s3fs
credentials_file = '/home/lorisadmin/.passwd-s3fs'

with open(credentials_file, 'w') as f:
    f.write(f"{access_key}:{secret_key}")

# Set the file permissions to be readable only by the owner
os.chmod(credentials_file, 0o600)
print(f"Credentials file '{credentials_file}' created and secured.")

# Step 3: Mount the MinIO bucket using s3fs
try:
    # The command to mount the bucket using s3fs
    mount_command = f"s3fs {bucket_name} {mount_point} -o passwd_file={credentials_file} -o url={minio_url} -o use_path_request_style -o allow_other"

    print(mount_command)

    # Run the command using subprocess
    result = subprocess.run(mount_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(f"Bucket '{bucket_name}' successfully mounted to '{mount_point}'.")
    else:
        print(f"Failed to mount the bucket: {result.stderr.decode('utf-8')}")
except subprocess.CalledProcessError as e:
    print(f"Error during mounting: {e.stderr.decode('utf-8')}")
