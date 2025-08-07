from sippy import SIP, Concept, QuantitativeValue
from sippy import LangString


# TODO: ContentCategory (wachten op sip.py mapping van mets/@TYPE)
# TODO: local identifiers (wachten op sip.py mapping van local id soort)
# TODO: secundaire titels


def get_mh_mapping(sip: SIP) -> dict:
    """
    Generate a mapping for the Material Artwork profile.
    """
    ie = sip.entity

    mapping = {
        "Descriptive": {
            "Title": get_nl_string(ie.name.root),
            "Description": get_nl_string(ie.description.root)
            if ie.description
            else None,
        },
        "Dynamic": {
            "dc_title": get_nl_string(ie.name.root),
            "dc_description": get_nl_string(ie.description.root)
            if ie.description
            else None,
            "dc_description_lang": get_nl_string(ie.description.root)
            if ie.description
            else None,
            "dcterms_created": ie.date_created.value,
            "dcterms_issued": ie.date_published.value if ie.date_published else None,
            "dc_rights_rightsOwners": [
                ("Auteursrechthouder", get_nl_string(owner.name.root))
                for owner in ie.copyright_holder
            ],
            "ContentCategory": "image",
            "dc_subjects": [
                ("Trefwoord", trefwoord)
                for trefwoord in get_nl_strings(ie.keywords.root)
            ]
            if ie.keywords
            else None,
            "dc_identifier_localid": ie.local_identifier[0].value
            if len(ie.local_identifier)
            else None,
            "dc_identifier_localids": [
                ("local_id", local_id.value) for local_id in ie.local_identifier
            ],
            "dc_languages": [("multiselect", lang) for lang in ie.in_language],
            "dc_titles": [("title", title.id) for title in ie.is_part_of],
            "dc_creators": [
                (creator.role_name, get_nl_string(creator.creator.name.root))
                for creator in ie.creator
                if creator.creator
            ],
            "dc_contributors": [
                (
                    contributor.role_name,
                    get_nl_string(contributor.contributor.name.root),
                )
                for contributor in ie.contributor
                if contributor.contributor
            ],
            "dc_publishers": [
                (publisher.role_name, get_nl_string(publisher.publisher.name.root))
                for publisher in ie.publisher
                if publisher.publisher
            ],
            "dc_types": [
                ("multiselect", genre) for genre in get_nl_strings(ie.genre.root)
            ]
            if ie.genre
            else None,
            "dc_coverages": [
                ("ruimte", get_nl_string(ruimte.name.root)) for ruimte in ie.spatial
            ]
            + [("tijd", tijd) for tijd in get_nl_strings(ie.temporal.root)]
            if ie.temporal
            else [],
            "artmedium": get_nl_string(ie.art_medium.root) if ie.art_medium else None,
            "artform": get_nl_string(ie.artform.root) if ie.artform else None,
            "dc_rights_credit": get_nl_string(ie.credit_text.root)
            if ie.credit_text
            else None,
            "dc_rights_comment": get_nl_string(ie.rights.root) if ie.rights else None,
            "dc_rights_licenses": get_licenses(sip),
            "dimensions": [
                ("width_in_mm", dimension_transform(ie.width) if ie.width else None),
                ("height_in_mm", dimension_transform(ie.height) if ie.height else None),
                ("depth_in_mm", dimension_transform(ie.depth) if ie.depth else None),
                ("weight_in_kg", dimension_transform(ie.weight) if ie.weight else None),
            ],
        },
    }

    return mapping


def dimension_transform(dimension: QuantitativeValue) -> str:
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


def get_nl_strings(strings: list[LangString]) -> list[str]:
    """
    Extract the Dutch language string from a list of LangStrings.

    Args:
        strings (list[LangString]): List of LangStrings.

    Returns:
        str: The value of the LangString with language 'nl'.
    """
    nl_strings = [lang_string for lang_string in strings if lang_string.lang == "nl"]

    return [nl_string.value for nl_string in nl_strings]


def get_nl_string(strings: list[LangString]) -> str:
    """
    Extract the Dutch language string from a list of LangStrings.

    Args:
        strings (list[LangString]): List of LangStrings.

    Returns:
        str: The value of the LangString with language 'nl'.
    """
    nl_strings = [lang_string for lang_string in strings if lang_string.lang == "nl"]

    return nl_strings[0].value


def get_licenses(sip: SIP) -> list[tuple[str, str]]:
    """
    Get the licenses for the Material Artwork profile.

    Returns:
        list[tuple[str, str]]: List of tuples containing license type and name.
    """
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
        ("multiselect", get_nl_string(license.pref_label.root))
        for license in sip.entity.license
        if type(license) is Concept
    ]
