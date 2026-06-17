from tortoise import fields, models

from app.accidents.value_sets import (
    AircraftDamage,
    FlightSchedule,
    InvestigationType,
    ReportStatus,
    Severity,
    WeatherCondition,
)


class Event(models.Model):
    id = fields.IntField(primary_key=True)
    event_id = fields.CharField(max_length=32, unique=True)
    event_date = fields.DateField(db_index=True)
    event_year = fields.SmallIntField(db_index=True)
    location = fields.CharField(max_length=128, null=True)
    country = fields.ForeignKeyField(
        "models.Country", related_name="events", null=True, on_delete=fields.SET_NULL
    )
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    airport_code = fields.CharField(max_length=16, null=True)
    airport_name = fields.CharField(max_length=128, null=True)
    weather_condition = fields.CharEnumField(enum_type=WeatherCondition, null=True)
    investigation_type = fields.CharEnumField(enum_type=InvestigationType)
    report_status = fields.CharEnumField(enum_type=ReportStatus, null=True)
    publication_date = fields.DateField(null=True)
    max_severity = fields.CharEnumField(enum_type=Severity, null=True)

    class Meta:
        table = "event"
        indexes = (("event_year", "latitude", "longitude"),)

    def __str__(self) -> str:
        return f"{self.event_id} ({self.event_year})"


class Aircraft(models.Model):
    id = fields.IntField(primary_key=True)
    accident_number = fields.CharField(max_length=32, unique=True)
    event = fields.ForeignKeyField(
        "models.Event", related_name="aircraft", on_delete=fields.CASCADE
    )
    registration_number = fields.CharField(max_length=32, null=True)
    manufacturer = fields.ForeignKeyField(
        "models.Manufacturer", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    model = fields.CharField(max_length=64, null=True)
    category = fields.ForeignKeyField(
        "models.AircraftCategory", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    amateur_built = fields.BooleanField(null=True)
    number_of_engines = fields.SmallIntField(null=True)
    engine_type = fields.ForeignKeyField(
        "models.EngineType", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    far_description = fields.ForeignKeyField(
        "models.FarDescription", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    schedule = fields.CharEnumField(enum_type=FlightSchedule, null=True)
    purpose = fields.ForeignKeyField(
        "models.FlightPurpose", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    air_carrier = fields.CharField(max_length=256, null=True)
    broad_phase_of_flight = fields.ForeignKeyField(
        "models.FlightPhase", related_name="aircraft", null=True, on_delete=fields.SET_NULL
    )
    aircraft_damage = fields.CharEnumField(enum_type=AircraftDamage, null=True)
    severity = fields.CharEnumField(enum_type=Severity, null=True)
    fatal_injuries = fields.SmallIntField(null=True)
    serious_injuries = fields.SmallIntField(null=True)
    minor_injuries = fields.SmallIntField(null=True)
    uninjured = fields.SmallIntField(null=True)

    class Meta:
        table = "aircraft"

    def __str__(self) -> str:
        return self.accident_number