#!/bin/bash

curl "http://localhost:8000/reservation/${spot_id}/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${token}" \
  --data '{
    "reservation": {
      "reservation_length": "'"${length}"'"
    }
  }'

echo
echo