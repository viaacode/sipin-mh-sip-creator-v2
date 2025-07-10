import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from sippy.objects import (
    DigitalRepresentation,
    File,
)

from sippy.sip import SIP


def get_jinja_template():
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    
    return env.get_template("base.jinja")


def generate_mets_from_sip(sip: SIP, pid: str, archive_location: str) -> str:
    """
    Generate a METS XML file from a SIP instance.
    """
    template = get_jinja_template()
    
    profile = str(sip.profile).split("/")[-1]
    version = str(sip.profile).split("/")[-2]
    
        
    files = []
    for representation_index, representation in enumerate(sip.entity.is_represented_by):
        if isinstance(representation, DigitalRepresentation):
            for file_index, file in enumerate(representation.includes):
                if isinstance(file, File):
                    # we need to make a MH media with a MH representation entry that corresponds to a dmd sec and filegroup
                    # for the filesice we need the checksum and we generate a ID based.
                    files.append({
                        "id": f"FILEID-{profile.upper()}-REPRESENTATION-{representation_index}-{file_index}",
                        "representation_index": representation_index,
                        "file_index": file_index,
                        "original_name": file.original_name,
                        "checksum": file.fixity,
                        "archive_location": archive_location,
                    })
        
    dmd_secs = []
    for file in files:
        dmd_secs.append({
            "id": file["id"].replace("FILEID", "DMDID"),
            "original_name": file["original_name"],
            "external_id": f"{pid}_{file['representation_index']}_{file['file_index']}",
            "pid": pid,
            "cp_id": sip.entity.maintainer.identifier,
            "sp_name": "sipin",
        })
    
    data = {
        "createdate": datetime.now().isoformat(),
        "profile": profile,
        "pid": pid,
        "files": files,
        "dmd_sections": dmd_secs,
        "ie": sip.entity,
        "events": sip.events,
        "archive_location": archive_location,
    }
    
    return template.render(data)
