from datetime import datetime
from pathlib import Path
from typing import Literal

from jinja2 import Environment, PackageLoader

import sippy

from sippy.sip import SIP

from . import profiles


def generate_mh_sidecar_dict(sip: sippy.SIP) -> dict:
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
    env = Environment(loader=PackageLoader(__name__))
    return env.get_template("base.jinja")


def generate_mets_from_sip(
    sip: SIP,
    pid: str,
    archive_location: Literal["Disk", "Tape"],
    mh_sidecar_version: str,
) -> str:
    """
    Generate a METS XML file from a SIP instance.
    """

    profile = str(sip.profile).split("/")[-1]
    template = get_jinja_template()

    files = []

    digital_representations = [
        r
        for r in sip.entity.is_represented_by
        if isinstance(r, sippy.DigitalRepresentation)
    ]
    for representation_index, representation in enumerate(digital_representations):
        for file_index, file in enumerate(representation.includes):
            if file.stored_at.file_path is None:
                raise ValueError(
                    "The file path on SIP.py File must be present in order to create a MediaHaven SIP."
                )

            file_path = Path(file.stored_at.file_path)
            file_name = file_path.name

            if file.fixity is None:
                raise ValueError(
                    "The fixity on SIP.py File must be present in order to create a MediaHaven SIP."
                )

            files.append(
                {
                    "id": f"FILEID-{profile.upper()}-REPRESENTATION-{representation_index}-{file_index}",
                    "representation_index": representation_index,
                    "file_index": file_index,
                    "original_name": file_name,
                    "checksum": file.fixity.value,
                    "archive_location": archive_location,
                }
            )

    sidecar = generate_mh_sidecar_dict(sip)

    dmd_secs = []
    for file in files:
        dmd_secs.append(
            {
                "id": file["id"].replace("FILEID", "DMDID"),
                "original_name": file["original_name"],
                "external_id": f"{pid}_{file['representation_index']}_{file['file_index']}",
                "pid": pid,
                "cp_id": sip.entity.maintainer.identifier,
                "sp_name": "sipin",
            }
        )

    data = {
        "mh_sidecar_version": mh_sidecar_version,
        "createdate": datetime.now().isoformat(),
        "profile": profile,
        "pid": pid,
        "files": files,
        "dmd_sections": dmd_secs,
        "ie": sip.entity,
        "events": sip.events,
        "archive_location": archive_location,
        "sidecar": sidecar,
    }

    return template.render(data)
