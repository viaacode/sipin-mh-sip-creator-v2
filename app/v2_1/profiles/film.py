from sippy import SIP, Concept

from . import common


def get_mh_mapping(sip: SIP) -> dict:
    common_fields = common.get_mh_mapping(sip)
    film_fields = {
        "Dynamic": {
            "ContentCategory": "image",  # TODO: which content category should this be?
        },
    }

    # TODO
    # "type_viaa": ie.format,

    return common.deepmerge(common_fields, film_fields)
