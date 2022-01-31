# Secure-My-Spot: Back-End

## \#TLDR
- This application offers a convenient way for users to locate, reserve, and pay for on-street 
  parking in New York City
- The app is a Dockerised Django / PostgreSQL back-end application
- The main resources are the User, Parking Spots, and Reservations, whereby there is a 1-to-Many 
  relationship between Users and Reservations and a 1-to-1 relationship between Reservations and 
  Parking Spots
- Polling of Django / PostgreSQL back-end ensures only available parking spots are displayed on 
  Google Map
- Users can pick an available parking spot and choose the length of the reservation period
- Custom in-app Stripe payments and processing flow, using setup intent and payment intent objects
- Reservation of parking spots is only confirmed upon successful completion of Stripe payment 
  processing whereby card details are collected for later charging
- Celery, RabbitMQ, and Redis are used to set up tasks that need to be executed at the end of 
  the reservation period 
- Users can change the reservation length or end a reservation at any time, either case results 
  in an email sent to the user to confirm any amendments to the reservation
- At the end of the reservation period the message broker pushes end-of-reservation tasks to 
  Celery for execution, including sending an end-of-reservation email to the user, changing the 
  state of the reserved parking spot resource from reserved to available in the PostgreSQL 
  backend, and using the Stripe setup intent and the customer's payment details to charge the 
  full amount
- Pytest has been used for unit testing / test-driven-development
- CD / CI pipeline is set up using GitHub workflows such that any branch that is pushed to 
  GitHub is automatically and fully tested and any successful pull requests or pushes into the 
  main branch are automatically deployed to Heroku

## Technologies used for the Front- and Back-End
| Technology            | Front-End | Back-End |
|:----------------------|:---------:|:--------:|
| Axios                 |     x     |          |
| Black                 |           |    x     |
| Bootstrap             |     x     |          |
| Camelcase             |     x     |          |
| Celery                |           |    x     |
| Coverage              |     x     |    x     |
| Crypto.js             |     x     |          |
| CSS/SCSS              |     x     |          |
| Docker                |     x     |    x     |
| Dotenv                |     x     |          |
| Django                |           |    x     |
| Django Rest Framework |           |    x     |
| Factory Boy           |           |    x     |
| Faker                 |     x     |    x     |
| Flake8                |           |    x     |
| Google Maps Api       |     x     |          |
| Gunicorn              |           |    x     |
| Heroku                |           |    x     |
| HTML5                 |     x     |          |
| Husky                 |     x     |          |
| iSort                 |           |    x     |
| JavaScript            |     x     |          |
| Jest                  |     x     |          |
| Lodash                |     x     |          |
| Logrocket             |     x     |          |
| Luxon                 |     x     |          |
| Model Bakery          |           |    x     |
| Moment                |     x     |          |
| Pipenv                |           |    x     |
| PostgreSQL            |           |    x     |
| Pytest                |           |    x     |
| Redis                 |           |    x     |
| React                 |     x     |          |
| React Router-Dom      |     x     |          |
| TypeScript            |     x     |          |
| Stripe Api            |     x     |    x     |
| Styled Components     |     x     |          |
| Whitenoise            |           |    x     |


## Set-up & Installation for Local Development
1. Fork and clone the repo
2. Run `pipenv install`
3. Create `.env` file, placing it inside the project root directory (same level as Dockerfile), 
   and declare the following environment variables:
   - local development var
     - ENV=development
   - db variables for django
     - DB_NAME
     - DB_USER
     - DB_PASSWORD 
     - DB_HOST="db"
     - DB_PORT="5432"
     - SECRET
   - db var for postgres db docker service
     - POSTGRES_USER
     - POSTGRES_PASSWORD
     - POSTGRES_DB
   - python settings
     - PYTHONUNBUFFERED="1"
     - PYTHONDONTWRITEBYTECODE="1"
   - Rabbitmq vars 
     - RABBITMQ_DEFAULT_USER
     - RABBITMQ_DEFAULT_PASS
   - Redis vars 
     - REDIS_PASSWORD
   - EMAIL server settings
     - EMAIL_USER
     - EMAIL_PASSWORD
   - Stripe keys
     - STRIPE_API_TEST_KEY
4. Start the Docker container with `docker-compose up -d --build` (Docker must be 
   installed)
5. The app is running on `localhost:8000/admin/`

## Systems Design Considerations
1. Data is mostly well structured, factual, and numeric -> *relational db*
2. Data volume is limited (fixed number of parkings spaces that can be booked across a finite 
   number of times per unit of time) -> *relational db*
3. Dependency on real time data processing (avoid double booking a parking spot) -> 
   *non-relational db*

### Conclusion
Given the limited booking volume and hence limited need for fast and reliable real-time 
processing of parking bay bookings a relational database management system is to be preferred. 
This project will use PostgreSQL, given the use of Django on the back-end and existing excellent 
support for PostgreSQL.

## Links
### Back-end
- [Deployed app](https://secure-my-spot-api.herokuapp.com/admin/)
- [Github repo](https://github.com/sven-gerlach/secure-my-spot-api)
- [Kanban](https://github.com/sven-gerlach/secure-my-spot-api/projects/1)
### Front-end
- [Deployed app](https://secure-my-spot-client.herokuapp.com)
- [Github repo](https://github.com/sven-gerlach/secure-my-spot-client)
- [Kanban](https://github.com/sven-gerlach/secure-my-spot-client/projects/1)

## Routes Summary
### User / Auth End-Points
| Verb   | URI        | Body        | Headers | Status Response | Response Body |
|:-------|:-----------|:------------|:--------|:----------------|:--------------|
| POST   | /sign-up   | Credentials | n/a     | 201, Created    | user details  |
| POST   | /sign-in   | Credentials | n/a     | 201             | token         |
| DELETE | /sign-out  | n/a         | Token   | 204             | n/a           |
| PATCH  | /change-pw | Credentials | Token   | 204             | n/a           |

### Parking Spot End-Points
| Verb | URI                             | Params                                   | Status Response | Response Body  |
|:-----|:--------------------------------|:-----------------------------------------|:----------------|:---------------|
| GET  | /available-parking-spots        | n/a                                      | 200             | parking spots  |
| GET  | /available-parking-spots-filter | ?lat=[?]&long=[?]&unit=[km/mil]&dist=[?] | 200             | parking spots  |

### Reservations End-Points
| Verb   | URI                                               | Body                      | Headers | Status Response | Response Body |
|:-------|:--------------------------------------------------|:--------------------------|:--------|:----------------|:--------------|
| GET    | /reservation-auth                                 | n/a                       | Token   | 200             | reservations  |
| GET    | /expired-reservations-auth                        | n/a                       | Token   | 200             | reservations  |
| GET    | /reservation-unauth:reservation_id/:email         | n/a                       | n/a     | 200             | reservation   |
| POST   | /reservation-auth/:parking_spot_id                | email, reservation length | Token   | 201             | reservation   |
| POST   | /reservation-unauth/:parking_spot_id              | email, reservation length | n/a     | 201             | reservation   |
| PATCH  | /update-reservation-auth/:reservation_id          | end_time                  | Token   | 200             | reservation   |
| PATCH  | /update-reservation-unauth/:reservation_id/:email | end_time                  |         | 200             | reservation   |
| DELETE | /delete-reservation-auth/:reservation_id          | n/a                       | Token   | 204             | n/a           |
| DELETE | /delete-reservation-unauth/:reservation_id/email  | n/a                       | Token   | 204             | n/a           |

### Payment End-Points
| Verb | URI                                                            | Body | Headers | Status Response | Response Body        |
|:-----|:---------------------------------------------------------------|:-----|:--------|:----------------|:---------------------|
| POST | /create-payment-intent-auth/:reservation_id                    | n/a  | Token   | 201             | Stripe client secret |
| POST | /create-payment-intent-unauth/:reservation_id/:email           | n/a  |         | 201             | Stripe client secret |
| GET  | /confirm-successful-setup-intent-auth/:reservation_id          | n/a  | Token   | 204             | n/a                  |
| GET  | /confirm-successful-setup-intent-unauth/:reservation_id/:email | n/a  |         | 204             | n/a                  |

## ERD
![ERD Image](./development/ERD.PNG)

## Next Steps
- [ ] Replace polling of back-end with a websocket design that allows for bi-directional 
  communication between the front- and the back-end
- [ ] This could also be used to verify emails before users are allowed to create an account or 
  make a reservation (unauthenticated users)
- [ ] Renew tokens after [24h] automatically