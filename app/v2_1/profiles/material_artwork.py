from sippy import SIP, Concept, LangStrings, QuantitativeValue, UniqueLangStrings


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
            "mh:Title": get_nl_string(ie.name),
            "mh:Description": get_optional_nl_string(ie.description),
        },
        "Dynamic": {
            "dc_title": get_nl_string(ie.name),
            "dc_description": get_optional_nl_string(ie.description),
            "dc_description_lang": get_nl_string(ie.description)
            if ie.description
            else None,  # TODO: what does this field mean?
            "dcterms_created": ie.date_created.value,
            "dcterms_issued": ie.date_published.value if ie.date_published else None,
            "dc_rights_rightsOwners": [
                ("Auteursrechthouder", get_nl_string(owner.name))
                for owner in ie.copyright_holder
            ],
            "ContentCategory": "image",
            "dc_subjects": [
                ("Trefwoord", trefwoord) for trefwoord in get_nl_strings(ie.keywords)
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
                (creator.role_name, get_nl_string(creator.creator.name))
                for creator in ie.creator
                if creator.creator
            ],
            "dc_contributors": [
                (
                    contributor.role_name,
                    get_nl_string(contributor.contributor.name),
                )
                for contributor in ie.contributor
                if contributor.contributor
            ],
            "dc_publishers": [
                (publisher.role_name, get_nl_string(publisher.publisher.name))
                for publisher in ie.publisher
                if publisher.publisher
            ],
            "dc_types": [("multiselect", genre) for genre in get_nl_strings(ie.genre)]
            if ie.genre
            else None,
            "dc_coverages": [
                ("ruimte", get_nl_string(ruimte.name)) for ruimte in ie.spatial
            ]
            + [("tijd", tijd) for tijd in get_nl_strings(ie.temporal)]
            if ie.temporal
            else [],
            "artmedium": get_optional_nl_string(ie.art_medium),
            "artform": get_optional_nl_string(ie.artform),
            "dc_rights_credit": get_optional_nl_string(ie.credit_text),
            "dc_rights_comment": get_optional_nl_string(ie.rights),
            "dc_rights_licenses": get_licenses(sip),
            "dimensions": [
                ("width_in_mm", quantitive_value_to_millimetres(ie.width)),
                ("height_in_mm", quantitive_value_to_millimetres(ie.height)),
                ("depth_in_mm", quantitive_value_to_millimetres(ie.depth)),
                ("weight_in_kg", quantitive_value_to_millimetres(ie.weight)),
            ],
        },
    }

    return mapping


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
