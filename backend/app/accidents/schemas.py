from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.accidents.value_sets import (
    AircraftDamage,
    InvestigationType,
    ReportStatus,
    Severity,
    WeatherCondition,
)


class AccidentMapItem(BaseModel):
    id: int
    event_id: str
    event_date: date
    latitude: float
    longitude: float
    location: str | None = None
    severity: Severity | None = None
    investigation_type: InvestigationType


class AccidentMapResponse(BaseModel):
    year: int
    total_count: int
    mapped_count: int
    items: list[AccidentMapItem]


class AircraftDetail(BaseModel):
    accident_number: str
    manufacturer: str | None = None
    model: str | None = None
    category: str | None = None
    engine_type: str | None = None
    number_of_engines: int | None = None
    aircraft_damage: AircraftDamage | None = None
    severity: Severity | None = None
    fatal_injuries: int | None = None
    serious_injuries: int | None = None
    minor_injuries: int | None = None
    uninjured: int | None = None
    broad_phase_of_flight: str | None = None
    purpose: str | None = None
    

class AccidentDetail(BaseModel):
    id: int
    event_id: str
    event_date: date
    location: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    airport_code: str | None = None
    airport_name: str | None = None
    weather_condition: WeatherCondition | None = None
    investigation_type: InvestigationType
    report_status: ReportStatus | None = None
    max_severity: Severity | None = None
    aircraft: list[AircraftDetail]


class FilterOptions(BaseModel):
    years: list[int]
    severities: list[str]
    countries: list[str]
    aircraft_categories: list[str]
    flight_purposes: list[str]
    flight_phases: list[str]