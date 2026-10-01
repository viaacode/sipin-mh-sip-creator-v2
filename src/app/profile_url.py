import sippy


type Profile = str
type Version = str


def parse_profile_url(sip: sippy.SIP) -> tuple[Profile, Version]:
    splitted = sip.profile.split("/")
    profile = splitted[-1]
    version = splitted[-2]

    return profile, version
