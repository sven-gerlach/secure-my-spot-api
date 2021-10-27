#!/bin/bash

curl "http://localhost:8000/available-parking-spots/" \
  --include \
  --request GET \
  --header "Content-Type: application/json" \

echo
echo
