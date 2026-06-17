from enum import Enum


class InvestigationType(str, Enum):
    ACCIDENT = "Accident"
    INCIDENT = "Incident"


class Severity(str, Enum):
    FATAL = "Fatal"
    NON_FATAL = "Non-Fatal"
    INCIDENT = "Incident"
    UNAVAILABLE = "Unavailable"


class AircraftDamage(str, Enum):
    DESTROYED = "Destroyed"
    SUBSTANTIAL = "Substantial"
    MINOR = "Minor"


class WeatherCondition(str, Enum):
    VMC = "VMC"
    IMC = "IMC"
    UNK = "UNK"


class ReportStatus(str, Enum):
    PROBABLE_CAUSE = "Probable Cause"
    FACTUAL = "Factual"
    PRELIMINARY = "Preliminary"
    FOREIGN = "Foreign"


class FlightSchedule(str, Enum):
    SCHEDULED = "SCHD"
    NON_SCHEDULED = "NSCH"
    UNKNOWN = "UNK"