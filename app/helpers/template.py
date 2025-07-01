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

def determine_archive_location(self, sip: SIP) -> str:
    """
    Determines the archive location for the SIP based on its maintainer.
    
    Args:
        sip (SIP): The SIP object containing metadata.
    
    Returns:
        str: The archive location path.
    """
    cp_id = sip.maintainer.identifier
    archive_location = self.config["storage"]["default_archive_location"]

    tape_content_partners = [
        or_id.strip().lower()
        for or_id in self.config["storage"]["tape_content_partners"].split(",")
    ]
    disk_content_partners = [
        or_id.strip().lower()
        for or_id in self.config["storage"]["disk_content_partners"].split(",")
    ]

    if cp_id.lower() in tape_content_partners:
        archive_location = "Tape"
    if cp_id.lower() in disk_content_partners:
        archive_location = "Disk"
        
    return archive_location


def generate_mets_from_sip(sip: SIP, pid: str) -> str:
    """
    Generate a METS XML file from a SIP instance.
    """
    template = get_jinja_template()
    
    profile = str(sip.profile).split("/")[-1]
    version = str(sip.profile).split("/")[-2]
    
    archive_location = determine_archive_location(sip)
        
    files = []
    for representation_index, representation in enumerate(sip.is_represented_by):
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
                        "checksum": file.fixity.value,
                    })
        
    dmd_secs = []
    for file in files:
        dmd_secs.append({
            "id": file["id"].replace("FILEID", "DMDID"),
            "original_name": file["original_name"],
            "external_id": f"{pid}_{file['representation_index']}_{file['file_index']}",
            "pid": pid,
            "cp_id": sip.maintainer.identifier,
            "sp_name": "sipin",
        })
    
    data = {
        "createdate": datetime.now().isoformat(),
        "profile": profile,
        "pid": pid,
        "files": files,
        "dmd_sections": dmd_secs,
        "ie": sip,
        "archive_location": archive_location,
    }
    
    return template.render(data)
