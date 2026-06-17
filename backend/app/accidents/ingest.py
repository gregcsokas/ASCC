from __future__ import annotations

import csv
import logging
import re
import sys
from datetime import date, datetime

from tortoise import Model, Tortoise, run_async

from app.accidents.lookup_tables import (
    AircraftCategory,
    Country,
    EngineType,
    FarDescription,
    FlightPhase,
    FlightPurpose,
    Manufacturer,
)
from app.accidents.models import Aircraft, Event

logger = logging.getLogger(__name__)

CSV_ENCODING = "iso-8859-1"
BATCH = 1000
SEVERITY_RANK = {"Fatal": 4, "Non-Fatal": 3, "Incident": 2, "Unavailable": 1}

def _clean(v: str | None) -> str | None:
    v = (v or "").strip()
    return v or None


def _to_int(v: str | None) -> int | None:
    v = _clean(v)
    if v is None:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def _to_date(v: str | None) -> date | None:
    v = _clean(v)
    if v is None:
        return None
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        return None


def _to_bool(v: str | None) -> bool | None:
    return {"Yes": True, "No": False}.get(_clean(v) or "", None)


def _severity_class(v: str | None) -> str | None:
    v = _clean(v)
    if v is None:
        return None
    base = re.sub(r"\(.*?\)", "", v).strip()
    return base if base in SEVERITY_RANK else None


async def _build_lookup(model: type[Model], names: set[str]) -> dict[str, int]:
    names = {n for n in names if n}
    if names:
        existing = set(await model.all().values_list("name", flat=True))
        to_create = [model(name=n) for n in names - existing]
        if to_create:
            await model.bulk_create(to_create, batch_size=BATCH)
    return dict(await model.all().values_list("name", "id"))


async def ingest(csv_path: str) -> dict:
    if await Event.all().exists():
        logger.warning("Event table is not empty.")
        return {"skipped": True}

    with open(csv_path, encoding=CSV_ENCODING, newline="") as f:
        rows = list(csv.DictReader(f))
    logger.info("Lines: %d", len(rows))

    countries = await _build_lookup(Country, {_clean(r["Country"]) for r in rows})
    categories = await _build_lookup(AircraftCategory, {_clean(r["Aircraft.Category"]) for r in rows})
    engines = await _build_lookup(EngineType, {_clean(r["Engine.Type"]) for r in rows})
    phases = await _build_lookup(FlightPhase, {_clean(r["Broad.Phase.of.Flight"]) for r in rows})
    fars = await _build_lookup(FarDescription, {_clean(r["FAR.Description"]) for r in rows})
    purposes = await _build_lookup(FlightPurpose, {_clean(r["Purpose.of.Flight"]) for r in rows})

    makes = {(_clean(r["Make"]) or "").upper() for r in rows}
    manufacturers = await _build_lookup(Manufacturer, makes)

    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["Event.Id"], []).append(r)

    events, skipped = [], 0
    for event_id, grp in groups.items():
        head = grp[0]
        ed = _to_date(head["Event.Date"])
        if ed is None:
            skipped += len(grp)
            continue
        sev_ranks = [SEVERITY_RANK.get(_severity_class(r["Injury.Severity"]) or "", 0) for r in grp]
        top = max(sev_ranks)
        max_sev = next((k for k, v in SEVERITY_RANK.items() if v == top), None) if top else None
        events.append(Event(
            event_id=event_id,
            event_date=ed,
            event_year=ed.year,
            location=_clean(head["Location"]),
            country_id=countries.get(_clean(head["Country"])),
            latitude=float(head["Latitude"]) if _clean(head["Latitude"]) else None,
            longitude=float(head["Longitude"]) if _clean(head["Longitude"]) else None,
            airport_code=_clean(head["Airport.Code"]),
            airport_name=_clean(head["Airport.Name"]),
            weather_condition=_clean(head["Weather.Condition"]),
            investigation_type=_clean(head["Investigation.Type"]) or "Accident",  # 5 üres -> domináns
            report_status=_clean(head["Report.Status"]),
            publication_date=_to_date(head["Publication.Date"]),
            max_severity=max_sev,
        ))
    await Event.bulk_create(events, batch_size=BATCH)
    event_pk = dict(await Event.all().values_list("event_id", "id"))
    logger.info("Event created: %d (skipped lines without date: %d)", len(events), skipped)

    aircraft = []
    for event_id, grp in groups.items():
        eid = event_pk.get(event_id)
        if eid is None:
            continue
        for r in grp:
            make = (_clean(r["Make"]) or "").upper()
            aircraft.append(Aircraft(
                accident_number=r["Accident.Number"],
                event_id=eid,
                registration_number=_clean(r["Registration.Number"]),
                manufacturer_id=manufacturers.get(make),
                model=_clean(r["Model"]),
                category_id=categories.get(_clean(r["Aircraft.Category"])),
                amateur_built=_to_bool(r["Amateur.Built"]),
                number_of_engines=_to_int(r["Number.of.Engines"]),
                engine_type_id=engines.get(_clean(r["Engine.Type"])),
                far_description_id=fars.get(_clean(r["FAR.Description"])),
                schedule=_clean(r["Schedule"]),
                purpose_id=purposes.get(_clean(r["Purpose.of.Flight"])),
                air_carrier=_clean(r["Air.Carrier"]),
                broad_phase_of_flight_id=phases.get(_clean(r["Broad.Phase.of.Flight"])),
                aircraft_damage=_clean(r["Aircraft.Damage"]),
                severity=_severity_class(r["Injury.Severity"]),
                fatal_injuries=_to_int(r["Total.Fatal.Injuries"]),
                serious_injuries=_to_int(r["Total.Serious.Injuries"]),
                minor_injuries=_to_int(r["Total.Minor.Injuries"]),
                uninjured=_to_int(r["Total.Uninjured"]),
            ))
    await Aircraft.bulk_create(aircraft, batch_size=BATCH)
    logger.info("Aircraft created: %d", len(aircraft))
    return {"events": len(events), "aircraft": len(aircraft), "skipped": skipped}


async def _main(csv_path: str) -> None:
    from app.core.database import TORTOISE_ORM
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        await ingest(csv_path)
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_async(_main(sys.argv[1]))