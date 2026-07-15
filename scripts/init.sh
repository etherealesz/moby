#!/bin/bash

read -p "What's your service name? " -r SERVICE_NAME
read -p "What's your service description? " -r SERVICE_DESCRIPTION

echo "Setting service name to: $SERVICE_NAME..."

kebab_case_service_name=$(echo "$SERVICE_NAME" | tr '[:upper:]' '[:lower:]')
kebab_case_service_name=${kebab_case_service_name// /-}

sed -i.bak \
  "s/name = \"fastapi-template\"/name = \"$kebab_case_service_name\"/" pyproject.toml && \
  rm pyproject.toml.bak

sed -i.bak \
  "s/description = \"fastapi-template description\"/description = \"$SERVICE_DESCRIPTION\"/" pyproject.toml && \
  rm pyproject.toml.bak

sed -i.bak \
  "s/  name: FastAPI Template/  name: $SERVICE_NAME/" files/config/*.yaml && \
  rm files/config/*.yaml.bak

rm -f scripts/init.sh
rm -f scripts/init.ps1

echo "Initialization complete, you're all set!"
echo "Note: Install dependencies on your own, we don't want to mess with how you manage your environment."
