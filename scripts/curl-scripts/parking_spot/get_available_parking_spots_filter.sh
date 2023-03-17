#!/bin/bash

curl "http://localhost:8000/available-parking-spots-filter?"`
      `"lat=40.767208&"`
      `"long=-73.992041&"`
      `"unit=km&"`
      `"dist=0.3" \
  --include \
  --request GET \
  --header "Content-Type: application/json" \

echo
echo
