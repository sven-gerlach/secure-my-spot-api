#!/bin/bash

curl "http://localhost:8000/sign-in/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "credentials": {
      "email": "s@sg.de",
      "password": "123"
    }
  }'

echo
echo