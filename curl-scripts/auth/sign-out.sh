#!/bin/bash

curl "http://localhost:8000/sign-out/" \
  --include \
  --request DELETE \
  --header "Content-Type: application/json" \
  --header "Authorization: Token ${token}"

echo
echo