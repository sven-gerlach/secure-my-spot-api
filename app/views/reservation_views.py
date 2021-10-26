"""
Module for all reservation views
"""

from rest_framework.views import APIView


class CreateReservationView(APIView):
    """
    Create a new reservation. If the user is not authenticated confirm that data includes the
    user's email and the reservation length (minutes) and the param includes the parking spot id
    """
    def post(self, request, parking_spot_id):
        """
        Post method is split between authenticated and unauthenticated users. In both cases,
        this method invokes data serialization and creates a new reservation resource.
        """

        if request.user.is_authenticated:
            print("user is authenticated", request.user)
            print(parking_spot_id)
        else:
            # if the user is not authenticated
            data = request.data["reservation"]
            email = data["email"]
            reservation_length = data["reservation_length"]
