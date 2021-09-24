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

if [ "$1" = "force" ]
then
  echo ------------Black------------
  docker exec api black secure_my_spot/ app/ --extend-exclude=migrations
  echo
  echo ------------iSort------------
  docker exec api isort secure_my_spot/ app/ --profile black
else
  echo ------------Black------------
  docker exec api black secure_my_spot/ app/ --extend-exclude=migrations --check
  echo
  echo ------------iSort------------
  docker exec api isort secure_my_spot/ app/ --profile black --check
fi