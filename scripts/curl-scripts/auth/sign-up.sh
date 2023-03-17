#!/bin/bash

curl "http://localhost:8000/sign-up/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "credentials": {
      "email": "'"${email}"'",
      "password": "'"${pw}"'",
      "password_confirmation": "'"${pw_conf}"'"
    }
  }'

echo
echo