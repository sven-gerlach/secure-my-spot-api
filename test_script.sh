#!/bin/bash

# execute all relevant tests
# Note: the api container needs to be running

docker exec api coverage run -m pytest
docker exec api flake8 secure_my_spot/ app/ --max-line-length=100 --exclude=__init__.py,migrations
docker exec api black secure_my_spot/ app/ --check --extend-exclude=migrations
docker exec api isort secure_my_spot/ app/ --check