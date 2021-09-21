#!/bin/bash

# execute all relevant tests inside Docker container and prior to pushing branch to remote repo
# all tests are executed again on the repo as part of the project's CI/CD pipeline

echo
echo ------------Pytest------------
docker exec api coverage run -m pytest
echo
echo ------------Flake8------------
docker exec api flake8 secure_my_spot/ app/ --max-line-length=100 --exclude=__init__.py,migrations
echo
echo ------------Black------------
docker exec api black secure_my_spot/ app/ --check --extend-exclude=migrations
echo
echo ------------iSort------------
docker exec api isort secure_my_spot/ app/ --check