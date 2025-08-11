import sippy
from . import mappings


def generate_mh_sidecar_dict(sip: sippy.SIP) -> dict[str, str | list[tuple[str, str]]]:
    profile = str(sip.profile).split("/")[-1]
    version = str(sip.profile).split("/")[-2]

    match version:
        case "2.1":
            version_module = mappings.v2_1
        case _:
            raise ValueError(f"Unsupported version: {version} or profile: {profile}")

    match profile:
        case "material-artwork":
            profile_module = version_module.material_artwork
        case "film":
            profile_module = version_module.film
        case "basic":
            profile_module = version_module.basic
        case _:
            raise ValueError(f"Unsupported profile: {profile} for version: {version}")

    return profile_module.get_mh_mapping(sip)
