#!/bin/bash

# Set the project ID
PROJECT_ID="qwiklabs-gcp-02-26b6d55e31b0"

# Set the name of the GCS bucket
BUCKET_NAME="qwiklabs-gcp-02-26b6d55e31b0"

# Get the list of all VM instances in the project
gcloud compute instances list --project "$PROJECT_ID"

# Create a CSV file in write mode
echo "Name,Zone,Ephemeral IP,Static IP,Machine Type" > instances.csv

# Iterate over the list of VM instances
for instance in $(gcloud compute instances list --project "$PROJECT_ID")
do
  # Get the public ephemeral and static IP addresses for the instance
  ip_addresses=$(gcloud compute instances describe "$instance" --project "$PROJECT_ID" --format="value(networkInterfaces.0.accessConfigs.0.natIP)")

  # Add the data for the instance to the CSV file
  echo "$instance,$(gcloud compute instances describe "$instance" --project "$PROJECT_ID" --format="value(zone)"),\"$ip_addresses\",,$(gcloud compute instances describe "$instance" --project "$PROJECT_ID" --format="value(machineType)")" >> instances.csv
done

# Upload the CSV file to the GCS bucket
gsutil cp instances.csv gs://"$BUCKET_NAME"

# Print a success message
echo "CSV file uploaded to GCS bucket."
