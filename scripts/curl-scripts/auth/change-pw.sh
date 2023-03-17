#!/bin/bash

curl "http://localhost:8000/change-pw/" \
  --include \
  --request PATCH \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${token}" \
  --data '{
    "credentials": {
      "password": "'"${pw}"'",
      "password_confirmation": "'"${pw_conf}"'"
    }
  }'

echo
echo