import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader

from sippy.objects import (
    DigitalRepresentation,
)

from sippy.sip import SIP

from .mapping import generate_mh_sidecar_dict
from .utils import MediaHavenCreatorError


def get_jinja_template(version: str):
    version_folder = f"v{version.replace('.', '_')}"

    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "templates",
        version_folder,
    )
    env = Environment(loader=FileSystemLoader(template_dir))

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
    version = str(sip.profile).split("/")[-2]

    template = get_jinja_template(version)

    files = []

    digital_representations = [
        r for r in sip.entity.is_represented_by if isinstance(r, DigitalRepresentation)
    ]
    for representation_index, representation in enumerate(digital_representations):
        for file_index, file in enumerate(representation.includes):
            if file.stored_at.file_path is None:
                raise MediaHavenCreatorError(
                    "The file path on SIP.py File must be present in order to create a MediaHaven SIP."
                )

            file_path = Path(file.stored_at.file_path)
            file_name = file_path.name

            if file.fixity is None:
                raise MediaHavenCreatorError(
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
