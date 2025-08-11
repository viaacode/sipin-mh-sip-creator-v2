from sippy import SIP
from sippy import LangString

#
# TODO: licenses
# TODO: ContentCategory (wachten op sip.py mapping van mets/@TYPE)
# TODO: local identifiers (wachten op sip.py mapping van local id soort)
# TODO: secundaire titels
# TODO: afmetingen
# TODO: rechtenverklaring & hergebruiksvoorwaarden


def get_mh_mapping(
    sip: SIP,
) -> dict[str, dict[str, str | list[tuple[str, str]] | None]]:
    mapping = {
        "Descriptive": {
            "Title": get_nl_strings(sip.entity.name.root),
            "Description": get_nl_strings(sip.entity.description.root),
        },
        "Dynamic": {
            "dcterms_created": sip.entity.date_created.value,
            "dcterms_issued": sip.entity.date_published.value
            if sip.entity.date_published
            else None,
            "dc_rights_rightsOwners": [
                ("Auteursrechthouder", get_nl_string(owner.name.root))
                for owner in sip.entity.copyright_holder
            ],
            "ContentCategory": "image",
            "dc_subjects": [
                ("Trefwoord", trefwoord)
                for trefwoord in get_nl_strings(sip.entity.keywords.root)
            ]
            if sip.entity.keywords
            else None,
            "dc_identifier_localid": sip.entity.local_identifier[0].value
            if len(sip.entity.local_identifier)
            else None,
            "dc_identifier_localids": [
                ("local_id", local_id.value) for local_id in sip.entity.local_identifier
            ],
            "dc_languages": [("multiselect", lang) for lang in sip.entity.in_language],
            "dc_titles": [("title", title.id) for title in sip.entity.is_part_of],
            "dc_creators": [
                (creator.role_name, get_nl_string(creator.creator.name.root))
                for creator in sip.entity.creator
            ],
            "dc_contributors": [
                (
                    contributor.role_name,
                    get_nl_string(contributor.contributor.name.root),
                )
                for contributor in sip.entity.contributor
            ],
            "dc_publishers": [
                (publisher.role_name, get_nl_string(publisher.publisher.name.root))
                for publisher in sip.entity.publisher
            ],
            "dc_types": [
                ("multiselect", genre)
                for genre in get_nl_strings(sip.entity.genre.root)
            ]
            if sip.entity.genre
            else None,
            "dc_coverages": [
                ("ruimte", get_nl_string(ruimte.name.root))
                for ruimte in sip.entity.spatial
            ]
            + [("tijd", tijd) for tijd in get_nl_strings(sip.entity.temporal.root)]
            if sip.entity.temporal
            else [],
            "artmedium": get_nl_string(sip.entity.art_medium.root)
            if sip.entity.art_medium
            else None,
            "artform": get_nl_string(sip.entity.artform.root)
            if sip.entity.artform
            else None,
            "dc_rights_credit": get_nl_string(sip.entity.credit_text.root)
            if sip.entity.credit_text
            else None,
            "dc_rights_comment": get_nl_string(sip.entity.rights.root)
            if sip.entity.rights
            else None,
        },
    }

    return mapping


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
