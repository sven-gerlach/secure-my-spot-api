"""
This module is being loaded automatically by Pytest. It includes all fixtures which are also
automatically loaded in any test suites that require them. Therefore, fixtures can be used in any
test function without the need for importing the fixture into the module.
"""

import pytest

from .factories import ParkingSpotFactory


@pytest.fixture()
def parking_spot():
    """
    A fixture function that creates on the db and returns a clean random parking spot instance in
    form of a django query object.
    """

    # create a parking spot instance and save it on the db
    return ParkingSpotFactory()
