from typing import Any

import sippy

from . import common
from . import helpers


def get_mh_mapping(sip: sippy.SIP) -> dict[str, Any]:
    common_fields = common.get_mh_mapping(sip)
    bibliographic_fields = {
        "Dynamic": {
            # The format the transformator derives from mods:typeOfResource
            # (#BICP30), e.g. 'newspaper' for a 'Newspaper Edition'.
            "type_viaa": sip.entity.format.value,
        },
    }

    return helpers.deepmerge(bibliographic_fields, common_fields)
