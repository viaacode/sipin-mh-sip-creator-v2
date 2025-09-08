from typing import TypedDict


class Descriptive(TypedDict):
    title: str
    description: str | None


Description = TypedDict(
    "Description",
    {
        "mh:Title": str,
        "mh:Description": str | None,
    },
)


class Dynamic(TypedDict):
    pass
    # dc_title
    # dc_description
    # dc_description_lang
    # dcterms_created
    # dcterms_issued
    # dc_rights_rightsOwners
    # ContentCategory
    # dc_subjects
    # dc_identifier_localid
    # dc_identifier_localids
    # dc_languages
    # dc_titles
    # dc_creators
    # dc_contributors
    # dc_publishers
    # dc_types
    # dc_coverages
    # artmedium
    # artform
    # dc_rights_credit
    # dc_rights_comment
    # dc_rights_licenses
    # dimensions


class Sidecare(TypedDict):
    Descriptive: Descriptive
    Dynamic: Dynamic
