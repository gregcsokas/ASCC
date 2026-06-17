from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from app.accidents.lookup_tables import AircraftCategory, Country, FlightPhase, FlightPurpose
from app.accidents.models import Aircraft, Event
from app.accidents.schemas import (
    AccidentDetail,
    AccidentMapItem,
    AccidentMapResponse,
    AircraftDetail,
    FilterOptions,
)
from app.accidents.value_sets import Severity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accidents", tags=["Accidents"])

@router.get("", response_model=AccidentMapResponse)
async def list_accidents(
    year: int = Query(..., ge=1900, le=2100, description="Event year"),
    severity: Severity | None = Query(None, description="Severity filter"),
    country: str | None = Query(None, description="Country filter"),
    category: str | None = Query(None, description="Aircraft category filter"),
    purpose: str | None = Query(None, description="Purpose filter"),
    phase: str | None = Query(None, description="Phase filter"),
) -> AccidentMapResponse:
    qs = Event.filter(event_year=year)

    if severity is not None:
        qs = qs.filter(max_severity=severity)
    if country is not None:
        qs = qs.filter(country__name=country)

    if category is not None or purpose is not None or phase is not None:
        aq = Aircraft.filter(event__event_year=year)
        if category is not None:
            aq = aq.filter(category__name=category)
        if purpose is not None:
            aq = aq.filter(purpose__name=purpose)
        if phase is not None:
            aq = aq.filter(broad_phase_of_flight__name=phase)
        event_ids = set(await aq.values_list("event_id", flat=True))
        qs = qs.filter(id__in=event_ids)

    total = await qs.count()
    mappable = qs.filter(latitude__isnull=False, longitude__isnull=False)
    mapped = await mappable.count()

    rows = await mappable.order_by("event_date").values(
        "id",
        "event_id",
        "event_date",
        "latitude",
        "longitude",
        "location",
        "max_severity",
        "investigation_type",
    )
    items = [
        AccidentMapItem(
            id=r["id"],
            event_id=r["event_id"],
            event_date=r["event_date"],
            latitude=r["latitude"],
            longitude=r["longitude"],
            location=r["location"],
            severity=r["max_severity"],
            investigation_type=r["investigation_type"],
        )
        for r in rows
    ]
    return AccidentMapResponse(
        year=year, total_count=total, mapped_count=mapped, items=items
    )


@router.get("/filters", response_model=FilterOptions)
async def get_filters() -> FilterOptions:
    years = sorted(await Event.all().distinct().values_list("event_year", flat=True))
    countries = sorted(await Country.all().values_list("name", flat=True))
    categories = sorted(await AircraftCategory.all().values_list("name", flat=True))
    purposes = sorted(await FlightPurpose.all().values_list("name", flat=True))
    phases = sorted(await FlightPhase.all().values_list("name", flat=True))
    
    return FilterOptions(
        years=years,
        severities=[s.value for s in Severity],
        countries=countries,
        aircraft_categories=categories,
        flight_purposes=purposes,
        flight_phases=phases,
    )


@router.get("/{event_id}", response_model=AccidentDetail)
async def get_accident(event_id: str) -> AccidentDetail:
    event = await Event.filter(event_id=event_id).select_related("country").first()
    if event is None:
        raise HTTPException(status_code=404, detail="Accident not found")

    aircraft_rows = await Aircraft.filter(event__event_id=event_id).values(
        "accident_number", "model", "number_of_engines",
        "aircraft_damage", "severity",
        "fatal_injuries", "serious_injuries", "minor_injuries", "uninjured",
        "manufacturer__name", "category__name", "engine_type__name",
        "broad_phase_of_flight__name", "purpose__name",
    )
    aircraft = [
        AircraftDetail(
            accident_number=a["accident_number"],
            manufacturer=a["manufacturer__name"],
            model=a["model"],
            category=a["category__name"],
            engine_type=a["engine_type__name"],
            number_of_engines=a["number_of_engines"],
            aircraft_damage=a["aircraft_damage"],
            severity=a["severity"],
            fatal_injuries=a["fatal_injuries"],
            serious_injuries=a["serious_injuries"],
            minor_injuries=a["minor_injuries"],
            uninjured=a["uninjured"],
            broad_phase_of_flight=a["broad_phase_of_flight__name"],
            purpose=a["purpose__name"],
        )
        for a in aircraft_rows
    ]
    return AccidentDetail(
        id=event.id,
        event_id=event.event_id,
        event_date=event.event_date,
        location=event.location,
        country=event.country.name if event.country else None,
        latitude=event.latitude,
        longitude=event.longitude,
        airport_code=event.airport_code,
        airport_name=event.airport_name,
        weather_condition=event.weather_condition,
        investigation_type=event.investigation_type,
        report_status=event.report_status,
        max_severity=event.max_severity,
        aircraft=aircraft,
    )