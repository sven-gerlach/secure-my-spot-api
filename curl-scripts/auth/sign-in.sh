#!/bin/bash

curl "http://localhost:8000/sign-in/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "credentials": {
      "email": "'"${email}"'",
      "password": "'"${pw}"'"
    }
  }'

echo
echo