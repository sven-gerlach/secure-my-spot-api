# Secure-My-Spot: Back-End

## TLDR
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
- Celery, RabbitMQ, and Redis are used to queue and process tasks that need to be executed at the end of 
  the reservation period, including payment processing with final bill amount, sending email to users confirming the end of the reservation period, changing a live reservation and all of its future queued processes
- Users can change the reservation length or end a reservation at any time, either case results 
  in an email sent to the user to confirm any amendments to the reservation
- At the end of the reservation period the message broker pushes end-of-reservation tasks to 
  Celery for execution, including sending an end-of-reservation email to the user, changing the 
  state of the reserved parking spot resource from reserved to available in the PostgreSQL 
  backend, and using the Stripe setup intent and the customer's payment details to charge the 
  full amount
- Pytest has been used for unit testing / test-driven-development
- A custom AWS EC2 instance has been set up to run the dockerised deployment environment, consisting of a Nginx reverse proxy, the django api, and a number of celery workers
- The deployed environment utilises cloud services, including RabbitMQ as the task queue manager, Redis as the task queue results storage, and an AWS RDS PostgreSQL instance (the dockerised development environment uses docker images for these three services instead)

## Technologies and Packages used for the Front- and Back-End
| Technology              | Front-End | Back-End |
|:------------------------|:---------:|:--------:|
| Axios                   |     x     |          |
| Black                   |           |    x     |
| Bootstrap               |     x     |          |
| Camelcase               |     x     |          |
| Celery                  |           |    x     |
| Certbot / Let's Encrypt |           |    x     |
| Coverage                |     x     |    x     |
| Crypto.js               |     x     |          |
| CSS/SCSS                |     x     |          |
| Docker                  |     x     |    x     |
| Django                  |           |    x     |
| Django Rest Framework   |           |    x     |
| Factory Boy             |           |    x     |
| Faker                   |     x     |    x     |
| Flake8                  |           |    x     |
| Google Maps Api         |     x     |          |
| Gunicorn                |           |    x     |
| Heroku                  |           |    x     |
| HTML5                   |     x     |          |
| Husky                   |     x     |          |
| iSort                   |           |    x     |
| JavaScript              |     x     |          |
| Jest                    |     x     |          |
| Lodash                  |     x     |          |
| Logrocket               |     x     |          |
| Luxon                   |     x     |          |
| Model Bakery            |           |    x     |
| Moment                  |     x     |          |
| Nginx                   |     x     |    x     |
| Pipenv                  |           |    x     |
| PostgreSQL              |           |    x     |
| Pytest                  |           |    x     |
| Redis                   |           |    x     |
| React                   |     x     |          |
| React Router-Dom        |     x     |          |
| TypeScript              |     x     |          |
| Stripe Api              |     x     |    x     |
| Styled Components       |     x     |          |
| Whitenoise              |           |    x     |


## Stack Overview
### Local Development Stack
This stack is defined in the [docker-compose.dev.yml](./docker-compose.dev.yml) file.
```mermaid
graph LR
  API[API]
  RQ[RabbitMQ]
  RR[Redis Results Backend]
  PG[(PostgreSQL)]
  subgraph CELERY [Celery]
    direction LR
    W1[Worker 1]
    W2[Worker 2]
    Wn[Worker n]
  end

  API --- RQ
  RQ --- CELERY
  API --- PG
  CELERY --- RR
  PG --- CELERY
```

### Deployed Stack
The stack inside the AWS EC2 instance is defined in the [docker-compose.deploy.yml](./docker-compose.deploy.yml) file. Redis is an instance on [Redis Cloud](https://app.redislabs.com/#/login). The RabbitMQ queue is an instance on [CloudAMQP](https://customer.cloudamqp.com/instance). The PostgreSQL database is hosted on AWS RDS.
```mermaid
graph LR
    C[Client]
    PG[PostgreSQL]
    subgraph AWS [AWS EC2]
        direction LR
        P[Proxy]
        CB[Certbot]
        API[API]
        subgraph CELERY [Celery]
            direction LR
            W1[Worker 1]
            W2[Worker 2]
            Wn[Worker n]
        end
    end
    RQ[RabbitMQ]
    RR[(Redis Celery Results Store)]

    C -- HTTPS --- P
    P -- HTTP --- API
    API --- RQ
    RQ --- CELERY
    CELERY --- RR
    API --- PG
    PG --- CELERY
```

## Set-up & Installation for Local Development
1. Clone this repo into your preferred local directory
2. Ensure pip, pipenv, and pyenv are installed locally (install pyenv with brew, pipenv with pip,
   and pip with `python -m ensurepip --upgrade`)
    > Use the following links for more detail on how to install these packages: 
    >- [pip](https://pip.pypa.io/en/stable/installation/)
    >- [pipenv](https://pipenv.pypa.io/en/latest/index.html#install-pipenv-today)
    >- [pyenv](https://github.com/pyenv/pyenv#homebrew-in-macos)
3. Ensure docker and docker-compose are installed in the local environment 
4. Run `pipenv install` in the project root directory to install all dependent packages
5. Install the Doppler CLI and authenticate according to these [instructions](https://docs.doppler.com/docs/install-cli)
6. Run the Doppler setup process in the root directory with `doppler setup`
7. Start the Postgres docker container with `doppler run -- docker-compose up -d --build`
8. Check containers are running normally by reviewing log statements with `docker logs [container_id]`
9. Run `pipenv shell` to initiate the environment (some IDE command lines will do this automatically)
10. Ensure the database has all the tables setup by running `docker exec [db_container_id] python manage.py migrate`
11. Confirm there are no outstanding migrations with `docker exec [db_container_id] python manage.py showmigrations`
12. Open the browser to review the [SPA](http://localhost:3000) and the [API](http://localhost:3001)

## Deployment
Below is a high-level summary of all deploy steps. Most of them only need to be applied once for the initial deployment.
1. Create EC2 instance
2. Create an elastic IP and associate it with the EC2 instance
3. Check DNS and verify that:
   1. AWS DNS is set up as the DNS server on Google Cloud (Google provides the domain sigmagamma.app)
   2. Route53 hosted zone sigmagamma.app has an A-record pointing to the EC2 elastic IP
4. Create key pair and store locally
5. Amend associated security group to allow access via SSH (22), HTTP (80) and HTTPS (443)
6. SSH into EC2 instance via `ssh -i /path/to/private-key.pem [EC2 Public IPv4 Address]`
7. Install docker, docker-compose, doppler, and git
8. Clone main branch into EC2 instance
9. Verify Redis Cloud, PostgreSQL AWS RDS, and RabbitMQ Cloud instances are running
10. Verify the environment variables stored in the Doppler prod config environment are correct
11. Run certify-init.sh `doppler run --token 'see Doppler secure-my-spot-api prod config' -- docker-compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh`
12. Stop all containers `doppler run --token 'token' -- docker-compose -f docker-compose.deploy.yml down`
13. Restart all containers `doppler run --token 'token' -- docker-compose -f docker-compose.deploy.yml up -d --build`

>**Note 1**: this [article](https://londonappdeveloper.com/django-docker-deployment-with-https-using-letsencrypt/) and this accompanying [YouTube](https://www.youtube.com/watch?v=3_ZJWlf25bY) video explain in detail how the containers can be configured to allow for HTTPS traffic. 

>**Note 2**: verify a cronjob is registered with `crontab -l`. A script needs to run once a week that runs the "certbot renew" command inside the certbot container. The command this cronjob runs is `doppler run --scope /home/ec2-user/secure-my-spot-api -- docker-compose -f docker-compose.deploy.yml run --rm certbot sh -c "certbot renew"` and essentially ensures that the https certificate with LetsEncrypt is renewed when needed (once a quarter). 

## Systems Design Considerations
1. Data is mostly well-structured, factual, and numeric -> *relational db*
2. Data volume is limited (fixed number of parking spaces that can be booked across a finite 
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
- [Deployed app](https://secure-my-spot.api.sigmagamma.com)
- [Github repo](https://github.com/sven-gerlach/secure-my-spot-api)
- [Kanban](https://github.com/sven-gerlach/secure-my-spot-api/projects/1)
### Front-end
- [Deployed app](https://www.secure-my-spot-spa.sigmagamma.app)
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

## Unresolved Issues
- [ ] When an admin enters their credentials into the [api's admin UI](https://secure-my-spot.api.sigmagamma.app/admin), the user sees an error ERR_TOO_MANY_REDIRECTS before they see the admin UI. When clicking on any path exposed in the admin UI, the user is beeing redirected to the log-in feature. The sessionID is stored in the db and in the browser cookie. Also, this error only ocurs in the production environment. It is likely caused by some mis-configuration of the nginx proxy and django's setting.py.

## Next Steps
- [ ] Replace polling of back-end with a websocket design that allows for bi-directional 
  communication between the front- and the back-end
- [ ] This could also be used to verify emails before users are allowed to create an account or 
  make a reservation (unauthenticated users)
- [ ] Renew tokens after [24h] automatically