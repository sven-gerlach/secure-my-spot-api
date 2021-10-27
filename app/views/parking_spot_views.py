"""
This module includes all the parking spots views
"""

from rest_framework import generics
from rest_framework.mixins import ListModelMixin

from utils.utils import haversine_distance

from ..models.parking_spot import ParkingSpot
from ..serializers.parking_spot_serializer import ParkingSpotSerializer


class GetAvailableParkingSpotsView(generics.ListAPIView, ListModelMixin):
    """
    View to list all available, that is unreserved, parking spots.

    * This is a public route that does not require token authentication
    """

    # query set containing all available parking spots that are commercially available (active)
    queryset = ParkingSpot.objects.filter(reserved=False, active=True)
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

        # query set containing all available parking spots that are commercially available (active)
        available_parking_spots = ParkingSpot.objects.filter(
            reserved=False, active=True
        )

        # retrieve query params; evaluation of query param completeness is overlooked as it is
        # assumed that the client front-end implementation will submit complete query strings
        # string values
        params = self.request.query_params
        lat = params["lat"]
        lng = params["lng"]
        unit = params["unit"]
        distance = params["dist"]

        # define a new filtered array of parking spot query sets
        available_parking_spots_filtered = []

        for parking_spot in available_parking_spots:
            if (
                haversine_distance(
                    user_lat=float(lat),
                    user_lng=float(lng),
                    parking_spot_lat=float(parking_spot.lat),
                    parking_spot_lng=float(parking_spot.lng),
                    unit=unit,
                )
                <= float(distance)
            ):
                available_parking_spots_filtered.append(parking_spot)

        return available_parking_spots_filtered
