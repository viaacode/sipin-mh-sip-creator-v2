from typing import Any
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

import sippy

from ..langstrings import get_nl_string, get_nl_strings, get_optional_nl_string


def get_mh_mapping(sip: sippy.SIP) -> dict[str, Any]:
    ie = sip.entity

    mapping = {
        "Descriptive": {
            "mh:Title": get_nl_string(ie.name),
            "mh:Description": get_optional_nl_string(ie.description),
        },
        "Dynamic": {
            "dc_title": get_nl_string(ie.name),
            "dc_description": get_optional_nl_string(ie.description),
            "dc_description_lang": get_optional_nl_string(ie.description),
            "dcterms_created": ie.date_created.value,
            "dcterms_issued": ie.date_published.value if ie.date_published else None,
            "dc_rights_rightsOwners": [
                ("Auteursrechthouder", get_nl_string(owner.name))
                for owner in ie.copyright_holder
            ],
            "dc_subjects": get_dc_subjects(ie),
            "dc_identifier_localid": get_dc_identifier_localid(ie),
            "dc_identifier_localids": get_dc_identifier_localids(ie),
            "dc_languages": [("multiselect", lang) for lang in ie.in_language],
            "dc_titles": get_dc_titles(ie),
            "dc_creators": get_creators(ie),
            "dc_contributors": get_contributors(ie),
            "dc_publishers": get_publishers(ie),
            "dc_types": get_dc_types(ie),
            "dc_coverages": get_coverages(ie),
            "artmedium": get_optional_nl_string(ie.art_medium),
            "artform": get_optional_nl_string(ie.artform),
            "dc_rights_credit": get_optional_nl_string(ie.credit_text),
            "dc_rights_comment": get_optional_nl_string(ie.rights),
            "dc_rights_licenses": get_licenses(sip),
            "dimensions": [
                ("width_in_mm", quantitive_value_to_millimetres(ie.width)),
                ("height_in_mm", quantitive_value_to_millimetres(ie.height)),
                ("depth_in_mm", quantitive_value_to_millimetres(ie.depth)),
                ("weight_in_kg", quantitive_value_to_millimetres(ie.weight)),
            ],
            #
            # Premis events
            "inspection_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/inspection"
            ),
            "inspection_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/inspection"
            ),
            "inspection_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/inspection"
            ),
            "repair_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/repair"
            ),
            "repair_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/repair"
            ),
            "repair_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/repair"
            ),
            "cleaning_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/cleaning"
            ),
            "cleaning_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/cleaning"
            ),
            "cleaning_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/cleaning"
            ),
            "baking_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/baking"
            ),
            "baking_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/baking"
            ),
            "baking_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/baking"
            ),
            "digitization_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/digitization"
            ),
            "digitization_time": get_event_time(
                sip, "https://data.hetarchief.be/id/event-type/digitization"
            ),
            "digitization_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/digitization"
            ),
            "digitization_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/digitization"
            ),
            "qc_date": get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/quality-control"
            ),
            "qc_outcome": get_event_outcome(
                sip, "https://data.hetarchief.be/id/event-type/quality-control"
            ),
            "qc_note": get_event_note(
                sip, "https://data.hetarchief.be/id/event-type/quality-control"
            ),
            "qc_by": get_event_implementer(
                sip, "https://data.hetarchief.be/id/event-type/quality-control"
            ),
            "ContentCategory": sip.mets_type,
        },
    }

    return mapping


def quantitive_value_to_millimetres(dimension: sippy.QuantitativeValue | None) -> str:
    if dimension is None:
        return "0"

    unit = dimension.unit_code
    value = dimension.value.value

    if unit == "MMT":
        return str(round(value))
    if unit == "CMT":
        return str(round(value * 10))
    if unit == "MTR":
        return str(round(value * 1000))

    if unit == "KGM":
        return str(value)

    return "0"


def get_licenses(sip: sippy.SIP) -> list[tuple[str, str]]:
    if len(sip.entity.license) == 0:
        return [
            ("multiselect", "VIAA-ONDERWIJS"),
            ("multiselect", "VIAA-ONDERZOEK"),
            ("multiselect", "VIAA-INTRA_CP-CONTENT"),
            ("multiselect", "VIAA-INTRA_CP-METADATA-ALL"),
            ("multiselect", "VIAA-PUBLIEK-METADATA-LTD"),
            ("multiselect", "BEZOEKERTOOL-CONTENT"),
            ("multiselect", "BEZOEKERTOOL-METADATA-ALL"),
        ]

    concepts = [
        ("multiselect", get_nl_string(license.pref_label))
        for license in sip.entity.license
        if isinstance(license, sippy.Concept)
    ]

    uris = [
        ("multiselect", license.id.split("/")[-1])
        for license in sip.entity.license
        if isinstance(license, sippy.URIRef)
    ]

    return concepts + uris


def get_dc_identifier_localids(
    entity: sippy.IntellectualEntity,
) -> list[tuple[str, str]]:
    return [
        (get_local_id_type(local_id), local_id.value)
        for local_id in entity.local_identifier
    ]


def get_dc_identifier_localid(entity: sippy.IntellectualEntity) -> str | None:
    return next((primary_id.value for primary_id in entity.primary_identifier), None)


def get_local_id_type(local_id: sippy.LocalIdentifier) -> str:
    local_id_url = local_id.type
    return Path(urlparse(local_id_url).path).name


def get_creators(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    creators = [
        (creator.role_name, get_nl_string(creator.creator.name))
        for creator in entity.creator
        if creator.creator
    ]
    return creators if len(creators) > 0 else None


def get_contributors(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    contributors = [
        (
            contributor.role_name,
            get_nl_string(contributor.contributor.name),
        )
        for contributor in entity.contributor
        if contributor.contributor
    ]

    return contributors if len(contributors) > 0 else None


def get_publishers(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    publishers = [
        (
            publisher.role_name,
            get_nl_string(publisher.publisher.name),
        )
        for publisher in entity.publisher
        if publisher.publisher
    ]

    return publishers if len(publishers) > 0 else None


def get_coverages(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    spatial = [("ruimte", get_nl_string(ruimte.name)) for ruimte in entity.spatial]
    temporal = (
        [("tijd", tijd) for tijd in get_nl_strings(entity.temporal)]
        if entity.temporal
        else []
    )

    coverages = spatial + temporal
    return coverages if len(coverages) > 0 else None


def get_dc_types(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    return (
        [("multiselect", genre) for genre in get_nl_strings(entity.genre)]
        if entity.genre
        else None
    )


def get_dc_subjects(entity: sippy.IntellectualEntity) -> list[tuple[str, str]] | None:
    return (
        [("Trefwoord", trefwoord) for trefwoord in get_nl_strings(entity.keywords)]
        if entity.keywords
        else None
    )


def get_event_with_type(
    sip: sippy.SIP, event_type: sippy.EventClass
) -> sippy.Event | None:
    for event in sip.events:
        if event.type == event_type:
            return event

    return None


def get_event_date(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    return datetime.fromisoformat(event.started_at_time.value).date().isoformat()


def get_event_time(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    return datetime.fromisoformat(event.started_at_time.value).time().isoformat()


def get_event_outcome(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    if event.outcome is None:
        return "n"

    match event.outcome.id:
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/fai":
            return "n"
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/suc":
            return "y"
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/war":
            return "y"


def get_event_note(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    return event.note


def get_quality_control_by(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    return get_nl_string(event.implemented_by.name)


def get_event_implementer(sip: sippy.SIP, event_type: sippy.EventClass) -> str | None:
    event = get_event_with_type(sip, event_type)
    if event is None:
        return None
    return get_nl_string(event.implemented_by.name)


def get_dc_titles(ie: sippy.IntellectualEntity) -> list[tuple[str, str]]:
    titles: list[tuple[str, str]] = []
    for item in ie.schema_is_part_of:
        match item:
            case sippy.BroadcastEvent():
                titles.append(("programma", get_nl_string(item.name)))
            case sippy.Newspaper():
                # Dit heeft geen mapping nodig naar dc_titles
                pass
            case sippy.CreativeWorkSeason():
                titles.append(("seizoen", get_nl_string(item.name)))
            case sippy.CreativeWorkSeries():
                titles.append(("serie", get_nl_string(item.name)))
            case sippy.ArchiveComponent():
                titles.append(("archief", get_nl_string(item.name)))
                sub_archives = [
                    sub
                    for sub in item.has_part
                    if isinstance(sub, sippy.ArchiveComponent)
                ]
                for sub_archive in sub_archives:
                    titles.append(("deelarchief", get_nl_string(sub_archive.name)))

            case sippy.Episode():
                titles.append(("aflevering", get_nl_string(item.name)))
            case sippy.CreativeWork():
                # Dit heeft geen mapping nodig naar dc_titles
                pass
            case _:
                raise NotImplementedError()

    return titles
