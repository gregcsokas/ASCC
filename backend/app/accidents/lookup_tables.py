from tortoise import fields, models


class LookupBase(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=128, unique=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class Country(LookupBase):
    class Meta:
        table = "country"


class AircraftCategory(LookupBase):
    class Meta:
        table = "aircraft_category"


class EngineType(LookupBase):
    class Meta:
        table = "engine_type"


class FlightPhase(LookupBase):
    class Meta:
        table = "flight_phase"


class FarDescription(LookupBase):
    class Meta:
        table = "far_description"


class FlightPurpose(LookupBase):
    class Meta:
        table = "flight_purpose"


class Manufacturer(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=128, unique=True)

    class Meta:
        table = "manufacturer"

    def __str__(self) -> str:
        return self.name