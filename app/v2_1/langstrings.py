from sippy import UniqueLangStrings, LangStrings


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
