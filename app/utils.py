from typing import Any

import sippy

from . import v2_1
from .mediahaven_sip import (
    MediahavenSip,
    MediahavenSipWriter,
    remove_mediahaven_sip_folder,
    zip_mediahaven_sip,
)
from .profile_url import parse_profile_url


def get_mets_creator(sip: sippy.SIP):
    _, version = parse_profile_url(sip)

    match version:
        case "2.1":
            return v2_1.create_mh_mets_data
        case _:
            raise ValueError(
                f"Received SIP.py SIP with invalid profile version '{version}'"
            )


def get_mediahaven_sip_writer(sip: sippy.SIP) -> MediahavenSipWriter:
    _, version = parse_profile_url(sip)

    match version:
        case "2.1":
            return v2_1.write_mediahaven_sip
        case _:
            raise ValueError(
                f"Received SIP.py SIP with invalid profile version '{version}'"
            )


def create_mediahaven_sip(
    sip: sippy.SIP, config: dict[str, Any], pid: str
) -> MediahavenSip:
    """
    Write the MediaHaven SIP, zip it, and remove the unzipped folder.
    """
    write_mediahaven_sip = get_mediahaven_sip_writer(sip)
    mh_sip = write_mediahaven_sip(sip, config, pid)
    zip_mediahaven_sip(mh_sip)
    remove_mediahaven_sip_folder(mh_sip)
    return mh_sip
