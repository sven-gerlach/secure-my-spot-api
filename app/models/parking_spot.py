"""
A model for parking spots that are part of the company's inventory for renting out to users
"""

from django.db import models


class ParkingSpot(models.Model):
    """
    A model that represents a parking spot

    Model Fields
    ----------------
    lat: decimal
        A number with 6 decimal places and bounded by [-90,90].
    lng: decimal
        A number with 6 decimal places and bounded by (-180,180]
        Note: albeit not overly relevant, an overlapping -180th or 180th meridian is being
        avoided by making the range exclusive on the negative 180 end and inclusive on the
        positive 180 end
    reserved: bool
        Indicates if parking spot is reserved or whether it is available for reserving
    active: bool
        False implies that the parking spot has been taken out of the commercially available
        pool. This necessary since parking spots that have been reserved in the past cannot be
        deleted (parking_spot foreign key on the reservation model has been set to
        on_delete=models.PROTECT. Instead of deleting parking spots the admin should instead
        render them inactive.
    rate: decimal
        A number with 2 decimal places. Indicates the hourly USD rate for a parking spot.

    Note: lat / lng nomenclature is the same as used by Google maps

    Methods
    -------------
    coordinates: str
        A getter method that returns a string representation of lat/long
        -> coordinates="51.432393,-0.348023"
    """

    lat = models.DecimalField(
        help_text="GPS latitude bounded by [-90,90] and with 6 decimals",
        decimal_places=6,
        max_digits=9,
    )

    lng = models.DecimalField(
        help_text="GPS longitude bounded by (-180, 180] with 6 decimals",
        decimal_places=6,
        max_digits=9,
    )

    reserved = models.BooleanField(
        help_text="Specifies if the parking spot is already reserved", default=False
    )

    active = models.BooleanField(
        help_text="Is the parking spot commercially available to users", default=True
    )

    rate = models.DecimalField(
        help_text="hourly rate in USD with 2 decimals", decimal_places=2, max_digits=5
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_coordinates(self) -> str:
        """
        Returns the coordinates in string format -> "lat,lng"
        """

        return f"{str(self.lat)},{str(self.lng)}"

    def __str__(self) -> str:
        """
        Return a string representation of the ParkingSpot instance
        """
        return (
            f"Parking spot {self.id}, located at ({self.lat},{self.lng}), "
            f"is {self.get_status} for an hourly rate of {self.rate}"
        )

    def get_dictionary(self, *args: str) -> dict:
        """
        Return a dictionary containing all the provided args as keys and their respective values
        """
        return {arg: getattr(self, arg) for arg in args}

    @property
    def get_status(self) -> str:
        """
        returns the string "reserved" if the reserved field attribute is True and "available"
        otherwise
        """
        return "reserved" if self.reserved else "available"
