# Secure-My-Spot: Back-End

## TLDR
[tbd]

## Set-up & Installation for Local Development
[tbd]

## Systems Design Considerations
1. Data is mostly well structured, factual, and numeric -> *relational db*
2. Data volume is limited (fixed number of parkings spaces that can be booked across a finite number of times per unit of time) -> *relational db*
3. Dependency on real time data processing (avoid double booking a parking spot) -> *non-relational db*

### Conclusion
Given the limited booking volume and hence limited need for fast and reliable real-time processing of parking bay bookings a relational database management system is to be preferred. This project will use PostgreSQL, given the use of Django on the back-end and existing excellent support for PostgreSQL.

## Links
### Back-end
- [Deployed app](https://secure-my-spot-api.herokuapp.com)
- [Github repo](https://github.com/sven-gerlach/secure-my-spot-api)
- [Kanban](https://github.com/sven-gerlach/secure-my-spot-api/projects/1)
### Front-end
- [Deployed app](https://secure-my-spot-client.herokuapp.com)
- [Github repo](https://github.com/sven-gerlach/secure-my-spot-client)
- [Kanban](https://github.com/sven-gerlach/secure-my-spot-client/projects/1)

## Technologies
[tbd]

## Routes Summary
### User / Auth end-points
Verb | URI | Body | Headers | Status Response | Response Body
--- | --- | --- | --- | --- | --- |
POST | /sign-up | Credentials | n/a | 201, Created | user details
[tbc]

### Reservation end-points
Verb | URI | Body | Headers | Status Response | Response Body
--- | --- | --- | --- | --- | --- |
[tbd] | /reserve
[tbc] | /payment
[tbc] | /cancel

#### /reserve
Params: spot_id, start_time, end_time
Return: reservation_id

#### /payment
Params: reservation_id
Note: use Stripe for checkout and payments processing
#### /cancel
Params: reservation_id

### Private end-points
Verb | URI | Body | Headers | Status Response | Response Body
--- | --- | --- | --- | --- | --- |
[tbd] | /find_nearest_spots
[tbc] | /calculate_payment

#### /find_nearest_spots
Params: current_location
Return: list of tuples with (spot_id, location)

#### /calculate_payment
Params: reservation_id

## ERD
![ERD Image](./development/ERD.PNG)