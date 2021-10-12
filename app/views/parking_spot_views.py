"""
This module includes all the parking spots views
"""
from rest_framework import generics
from rest_framework.mixins import ListModelMixin

from ..models.parking_spot import ParkingSpot
from ..serializers.parking_spot_serializer import ParkingSpotSerializer


class GetAllParkingSpotsView(generics.ListAPIView, ListModelMixin):
    """
    View to list all available, that is unreserved, parking spots.

    * This is a public route that does not require token authentication
    """

    queryset = ParkingSpot.objects.filter(reserved=False)
    serializer_class = ParkingSpotSerializer
