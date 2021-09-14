curl "http://localhost:8000/sign-up/" \
  --include \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{
    "credentials": {
      "email": "test@test.de",
      "password": "1234",
      "password_confirmation": "1234"
    }
  }'

echo
echo