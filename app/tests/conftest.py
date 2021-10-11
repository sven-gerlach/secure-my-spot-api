"""
Parking spot instances
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
