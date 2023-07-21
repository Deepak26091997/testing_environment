import datetime
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import io
import os
import json
from google.cloud import storage
from google.cloud import secretmanager


# Set the scopes for the service account
SCOPES = ["https://www.googleapis.com/auth/compute.readonly"]

#################################################################
# Using Secret Manager
client = secretmanager.SecretManagerServiceClient()
name = f"projects/qwiklabs-gcp-02-26b6d55e31b0/secrets/secret.json/versions/latest"
#################################################################

response = client.access_secret_version(name=name)
creds_json = response.payload.data.decode('UTF-8')
creds_dict = json.loads(creds_json)

creds = service_account.Credentials.from_service_account_info(info=creds_dict, scopes=SCOPES)

# Get the list of all VM instances in the project
compute_service = build("compute", "v1", credentials=creds)
response = compute_service.instances().list(project="project_id").execute()
instances = response["items"]

# Create a list to store the data for the CSV file
data = []

# Iterate over the list of VM instances
for instance in instances:
    # Get the public ephemeral and static IP addresses for the instance
    ip_addresses = instance.get("networkInterfaces", [])[0].get("accessConfigs", [])
    ip_address = []
    for i in ip_addresses:
        ip_address.append(i.get("natIP", ""))

    # Add the data for the instance to the list
    data.append([
        instance.get("name"),
        instance.get("zone"),
        ip_address[0],
        ip_address[1]
    ])

# Create a CSV file in write mode
with io.open("instances.csv", "w", newline="") as csvfile:
    # Create a CSV writer object
    writer = csv.writer(csvfile, delimiter=",")

    # Write the header row
    writer.writerow(["Name", "Zone", "Ephemeral IP", "Static IP"])

    # Write the data rows
    writer.writerows(data)

# Upload the CSV file to the GCS bucket
bucket_name = "qwiklabs-gcp-02-26b6d55e31b0"
blob_name = "instances.csv"
storage_client = storage.Client()
blob = storage_client.bucket(bucket_name).blob(blob_name)
blob.upload_from_file("instances.csv")

print("CSV file uploaded to GCS bucket.")
