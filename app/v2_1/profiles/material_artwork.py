from typing import Any

from sippy import SIP, Concept, LangStrings, QuantitativeValue, UniqueLangStrings

from . import common
from . import helpers


def get_mh_mapping(sip: SIP) -> dict[str, Any]:
    common_fields = common.get_mh_mapping(sip)
    material_artwork_fields = {
        "Dynamic": {},
    }

    return helpers.deepmerge(common_fields, material_artwork_fields)


def quantitive_value_to_millimetres(dimension: QuantitativeValue | None) -> str:
    if dimension is None:
        return "0"

    unit = dimension.unit_code
    value = dimension.value.value

    if unit == "MMT":
        return str(round(value))
    if unit == "CMT":
        return str(round(value * 10))
    if unit == "MTR":
        return str(round(value * 1000))

    if unit == "KGM":
        return str(value)

    return "0"


def get_nl_strings(strings: LangStrings | UniqueLangStrings) -> list[str]:
    return [
        lang_string.value for lang_string in strings.root if lang_string.lang == "nl"
    ]


def get_nl_string(strings: LangStrings | UniqueLangStrings) -> str:
    return next(
        lang_string.value for lang_string in strings.root if lang_string.lang == "nl"
    )


def get_optional_nl_string(
    strings: LangStrings | UniqueLangStrings | None,
) -> str | None:
    if strings is None:
        return None
    return get_nl_string(strings)


def get_licenses(sip: SIP) -> list[tuple[str, str]]:
    if len(sip.entity.license) == 0:
        return [
            ("multiselect", "VIAA-ONDERWIJS"),
            ("multiselect", "VIAA-ONDERZOEK"),
            ("multiselect", "VIAA-INTRA_CP-CONTENT"),
            ("multiselect", "VIAA-INTRA_CP-METADATA-ALL"),
            ("multiselect", "VIAA-PUBLIEK-METADATA-LTD"),
            ("multiselect", "BEZOEKERTOOL-CONTENT"),
            ("multiselect", "BEZOEKERTOOL-METADATA-ALL"),
        ]

    return [
        ("multiselect", get_nl_string(license.pref_label))
        for license in sip.entity.license
        if isinstance(license, Concept)
    ]
