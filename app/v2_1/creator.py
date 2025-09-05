from datetime import datetime
from pathlib import Path
from typing import Literal
from typing import Any
import shutil
import zipfile

from jinja2 import Environment, PackageLoader

import sippy

from app.v2_1.langstrings import get_nl_string

from . import profiles


def create_mh_sidecar_data(sip: sippy.SIP) -> dict:
    splitted = sip.profile.split("/")
    profile = splitted[-1]
    version = splitted[-2]

    match profile:
        case "material-artwork":
            profile_module = profiles.material_artwork
        case "film":
            profile_module = profiles.film
        case "basic":
            profile_module = profiles.basic
        case _:
            raise ValueError(f"Unsupported profile '{profile}' for version '{version}'")

    return profile_module.get_mh_mapping(sip)


def get_jinja_template():
    """
    Gets the `templates/base.jinja` within the current package.
    """
    env = Environment(
        loader=PackageLoader(__name__),
        autoescape=True,
    )
    return env.get_template("base.jinja")


def create_mh_mets_data(
    sip: sippy.SIP,
    pid: str,
    archive_location: Literal["Disk", "Tape"],
    mh_sidecar_version: str,
) -> dict[str, Any]:
    """
    Create the data needed to render a METS XML file.
    """

    profile = str(sip.profile).split("/")[-1]

    files = []

    digital_representations = [
        r
        for r in sip.entity.is_represented_by
        if isinstance(r, sippy.DigitalRepresentation)
    ]
    for rep_idx, representation in enumerate(digital_representations):
        for file_idx, file in enumerate(representation.includes):
            if file.stored_at.file_path is None:
                raise ValueError(
                    "The file path on SIP.py File must be present in order to create a MediaHaven SIP."
                )

            if file.fixity is None:
                raise ValueError(
                    "The fixity on SIP.py File must be present in order to create a MediaHaven SIP."
                )

            file_path = Path(file.stored_at.file_path)
            file_name = file_path.name

            files.append(
                {
                    #
                    # file section
                    "id": f"FILEID-{profile.upper()}-REPRESENTATION-{rep_idx}-{file_idx}",
                    "original_name": file_name,
                    "checksum": file.fixity.value,
                    "archive_location": archive_location,
                    "source_href": file_path,
                    "href": f"representation_{rep_idx}/{file_name}",
                    #
                    # file DMD section
                    "dmd_id": f"DMDID-{profile.upper()}-REPRESENTATION-{rep_idx}-{file_idx}",
                    "external_id": f"{pid}_{rep_idx}_{file_idx}",
                    "pid": pid,
                    "cp_id": sip.entity.maintainer.identifier,
                    "sp_name": "sipin",
                }
            )

    sidecar = create_mh_sidecar_data(sip)

    events = [transform_event(event) for event in sip.events]

    return {
        "mh_sidecar_version": mh_sidecar_version,
        "createdate": datetime.now().isoformat(),
        "profile": profile,
        "pid": pid,
        "files": files,
        "ie": sip.entity,
        "events": events,
        "amdid": " ".join(event["mets_id"] for event in events),
        "archive_location": archive_location,
        "sidecar": sidecar,
    }


def write_mediahaven_sip(sip: sippy.SIP, config: dict[str, Any], pid: str) -> None:
    mh_sidecar_version = config["mh_sidecar_version"]
    aip_folder = config["aip_folder"]
    archive_location = determine_archive_location(sip, config)
    mets_data = create_mh_mets_data(sip, pid, archive_location, mh_sidecar_version)

    template = get_jinja_template()
    mets_xml = template.render(mets_data)
    mh_sip_path = Path(aip_folder) / pid

    mh_sip_path.mkdir(parents=True, exist_ok=True)
    mets_file_path = mh_sip_path / "mets.xml"
    with open(mets_file_path, "w") as mets_file:
        mets_file.write(mets_xml)

    for file in mets_data["files"]:
        dest_href = mh_sip_path / Path(file["href"])
        dest_href.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file["source_href"], dest_href)

    with zipfile.ZipFile(mh_sip_path.with_suffix(".zip"), "w") as zf:
        for path in mh_sip_path.rglob("*"):
            zf.write(path, arcname=path.relative_to(mh_sip_path))

    # Cleanup is default, but for testing it is usefull disable it
    should_cleanup = config.get("cleanup_sip", True)
    if should_cleanup:
        shutil.rmtree(mh_sip_path)


def determine_archive_location(
    sip: sippy.SIP, config: dict[str, Any]
) -> Literal["Disk", "Tape"]:
    """
    Determines the archive location for the SIP based on its maintainer.
    """
    cp_id = sip.entity.maintainer.identifier

    tape_content_partners = [
        or_id.strip().lower()
        for or_id in config["storage"]["tape_content_partners"].split(",")
    ]
    disk_content_partners = [
        or_id.strip().lower()
        for or_id in config["storage"]["disk_content_partners"].split(",")
    ]

    if cp_id.lower() in tape_content_partners:
        return "Tape"
    elif cp_id.lower() in disk_content_partners:
        return "Disk"

    archive_location = config["storage"]["default_archive_location"]
    return archive_location


def transform_event(event: sippy.Event) -> dict[str, Any]:
    return {
        "mets_id": "PREMIS-ID-" + event.id.split("/")[-1],
        "identifier": {
            "type": "UUID",
            "value": event.id.split("/")[-1],
        },
        "type": event.type.split("/")[-1],
        "datetime": event.started_at_time.value,
        "detail": event.note,
        "outcome": map_event_outcome(event.outcome),
        "outcome_note": event.outcome_note,
        "agents": get_event_agents(event),
        "objects": get_event_objects(event),
    }


def map_event_outcome(outcome: sippy.URIRef[sippy.EventOutcome] | None) -> str | None:
    if outcome is None:
        return None
    match outcome.id:
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/suc":
            return "success"
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/war":
            return "warning"
        case "http://id.loc.gov/vocabulary/preservation/eventOutcome/fai":
            return "fail"


def get_event_agents(event: sippy.Event) -> list[dict[str, str]]:
    implementer_agent = [
        {
            "type": "Implementer name",
            "value": get_nl_string(event.implemented_by.name),
            "role": "implementer",
        }
    ]
    executing_agent = (
        [
            {
                "type": "Executing program name",
                "value": get_nl_string(event.executed_by.name),
                "role": "executing program",
            }
        ]
        if event.executed_by
        else []
    )
    instrument_agents = [
        {
            "type": "Instrument name",
            "value": get_nl_string(instrument.name),
            "role": "instrument",
        }
        for instrument in event.instrument
    ]
    associated_agents = [
        {
            "type": "Agent name",
            "value": get_nl_string(associated_with.name),
            "role": "associated",
        }
        for associated_with in event.was_associated_with
    ]

    return implementer_agent + executing_agent + instrument_agents + associated_agents


def get_event_objects(event: sippy.Event) -> list[dict[str, str]]:
    results = [
        {
            "type": "UUID",
            "value": result.id,
            "role": "outcome",
        }
        for result in event.result
    ]
    sources = [
        {
            "type": "UUID",
            "value": source.id,
            "role": "source",
        }
        for source in event.source
    ]

    total = results + sources
    if len(total) == 0:
        return [
            {
                "type": "UUID",
                "value": "MH required at least one linking object on events",
                "role": "placeholder",
            }
        ]

    return total
