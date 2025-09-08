from typing import Any
from collections.abc import Callable
from pathlib import Path

import sippy

from . import v2_1


class MediaHavenCreatorError(Exception): ...


type Profile = str
type Version = str


def parse_profile_url(sip: sippy.SIP) -> tuple[Profile, Version]:
    splitted = sip.profile.split("/")
    profile = splitted[-1]
    version = splitted[-2]

    return profile, version


def get_mets_creator(sip: sippy.SIP):
    _, version = parse_profile_url(sip)

    match version:
        case "2.1":
            return v2_1.create_mh_mets_data
        case _:
            raise ValueError(
                f"Received SIP.py SIP with invalid profile version '{version}'"
            )


def get_sip_creator(
    sip: sippy.SIP,
) -> Callable[[sippy.SIP, dict[str, Any], str], tuple[Path, str]]:
    _, version = parse_profile_url(sip)

    match version:
        case "2.1":
            return v2_1.write_mediahaven_sip
        case _:
            raise ValueError(
                f"Received SIP.py SIP with invalid profile version '{version}'"
            )
