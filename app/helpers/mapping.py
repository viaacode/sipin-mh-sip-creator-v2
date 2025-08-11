import sippy
from . import mappings


def generate_mh_sidecar_dict(sip: sippy.SIP) -> dict[str, str | list[tuple[str, str]]]:
    profile = str(sip.profile).split("/")[-1]
    version = str(sip.profile).split("/")[-2]

    if version == "2.0":
        if profile == "material-artwork":
            mapping_function = mappings.v2_0.material_artwork.get_mh_mapping
        elif profile == "basic":
            mapping_function = mappings.v2_0.basic.get_mh_mapping
        else:
            raise ValueError(f"Unsupported profile: {profile} for version: {version}")
    elif version == "2.1":
        if profile == "material-artwork":
            mapping_function = mappings.v2_1.material_artwork.get_mh_mapping
        elif profile == "film":
            mapping_function = mappings.v2_1.film.get_mh_mapping
        elif profile == "basic":
            mapping_function = mappings.v2_1.basic.get_mh_mapping
        else:
            raise ValueError(f"Unsupported profile: {profile} for version: {version}")
    else:
        raise ValueError(f"Unsupported version: {version} or profile: {profile}")

    return mapping_function(sip)
