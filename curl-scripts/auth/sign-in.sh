#!/bin/bash

# Note: This sign-in script does not work anymore. This is due to the usage of hash keys on the
# front-end. Whilst the user may type in a password such as "123", the password sent via json to
# the api is in fact the hashed value of "123".

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