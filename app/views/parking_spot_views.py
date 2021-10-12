"""
This module includes all the parking spots views
"""
from rest_framework import generics
from rest_framework.mixins import ListModelMixin

from ..models.parking_spot import ParkingSpot
from ..serializers.parking_spot_serializer import ParkingSpotSerializer

from utils.utils import haversine_distance
from decimal import Decimal


class GetAvailableParkingSpotsView(generics.ListAPIView, ListModelMixin):
    """
    View to list all available, that is unreserved, parking spots.

    * This is a public route that does not require token authentication
    """

    queryset = ParkingSpot.objects.filter(reserved=False)
    serializer_class = ParkingSpotSerializer
    # turning pagination off
    pagination_class = None


class GetAvailableParkingSpotsFilterView(generics.ListAPIView, ListModelMixin):
    """
    View to list all available parking spots within a user specified radius.

    * This is a public route that does not require token authentication
    """

    # queryset = ParkingSpot.objects.filter(reserved=False)
    serializer_class = ParkingSpotSerializer
    pagination_class = None

    def get_queryset(self):
        """
        Filter queryset of available parking spots. The query_params will reveal the filtering
        conditions. The request url could look like this:
        available-parking-spots-radial-filter?lat=0.123456&long=0.123456&unit=km&dist=0.2
        available-parking-spots-radial-filter?lat=0.123456&long=0.123456&unit=miles&dist=0.1
        """

        # query set containing all available parking spots
        available_parking_spots = ParkingSpot.objects.filter(reserved=False)
        print(available_parking_spots)

        # retrieve query params; evaluation of query param completeness is overlooked as it is
        # assumed that the client front-end implementation will submit complete query strings
        # string values
        params = self.request.query_params
        latitude = params["lat"]
        longitude = params["long"]
        unit = params["unit"]
        distance = params["dist"]

        # define a new filtered array of parking spot query sets
        available_parking_spots_filtered = []

        for parking_spot in available_parking_spots:
            if haversine_distance(
                user_latitude=float(latitude),
                user_longitude=float(longitude),
                parking_spot_latitude=float(parking_spot.latitude),
                parking_spot_longitude=float(parking_spot.longitude),
                unit=unit
            ) <= float(distance):
                available_parking_spots_filtered.append(parking_spot)

        return available_parking_spots_filtered
