#!/bin/bash

curl "http://localhost:8000/reservation/${res_id}/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "reservation": {
      "email": "'"${email}"'",
      "reservation_length": "'"${length}"'"
    }
  }'

echo
echo