from typing import Any

from sippy import SIP

from . import common
from . import helpers


def get_mh_mapping(sip: SIP) -> dict[str, Any]:
    common_fields = common.get_mh_mapping(sip)
    basic_fields = {
        "Dynamic": {
            "ContentCategory": "image",  # TODO
        },
    }

    return helpers.deepmerge(common_fields, basic_fields)
