from typing import Any, Literal
from itertools import chain

import sippy


from . import common
from . import helpers

from .common import get_nl_string


def get_mh_mapping(sip: sippy.SIP) -> dict[str, Any]:
    carrier_rep = get_carrier_representation(sip.entity)
    physical_carrier = get_physical_carrier(carrier_rep)
    common_fields = common.get_mh_mapping(sip)

    fields = {
        "Dynamic": {
            #
            # Carrier representation
            "num_reels": get_number_of_reels(carrier_rep),
            #
            # Intellectual entity
            # "ContentCategory": "image",  # TODO: which content category should this be?
            "type_viaa": sip.entity.format.value,
            "image_sound": get_image_sound(sip.entity),
            #
            # Physical carrier
            "preservation_problems": get_preservation_problems(physical_carrier),
            "film_base": physical_carrier.material,
            # "dc_description_cast": hascastmember # TODO
            "subtitles": get_subtitles(physical_carrier),
            "language_subtitles": get_language_subtitles(physical_carrier),
            #
            # Image and audio reels
            "gauge": get_gauge(physical_carrier),
            "material_type": get_material_type(physical_carrier),
            "aspect_ratio": get_aspect_ratio(physical_carrier),
            "brand_of_film_stock": get_brand_of_film_stock(physical_carrier),
            #
            # Image Reel
            "color_or_bw": get_color_or_bw(physical_carrier),
        },
    }

    return helpers.deepmerge(fields, common_fields)


def get_carrier_representation(
    entity: sippy.IntellectualEntity,
) -> sippy.CarrierRepresentation:
    carrier_reps = [
        rep
        for rep in entity.is_represented_by
        if isinstance(rep, sippy.CarrierRepresentation)
    ]
    if len(carrier_reps) != 1:
        raise ValueError("Film must have exactly one carrier representation.")
    return carrier_reps[0]


def get_physical_carrier(
    carrier_rep: sippy.CarrierRepresentation,
) -> sippy.AnyPhysicalCarrier:
    if len(carrier_rep.stored_at) != 1:
        raise ValueError(
            "The Mediahaven METS only has space for the metadata of one physical carrier or reel."
        )
    return carrier_rep.stored_at[0]


def get_number_of_reels(rep: sippy.CarrierRepresentation) -> int | None:
    return rep.number_of_reels.value if rep.number_of_reels else None


def get_preservation_problems(
    carrier: sippy.AnyPhysicalCarrier,
) -> list[tuple[str, str]] | None:
    problems = [get_nl_string(prob.pref_label) for prob in carrier.preservation_problem]
    return [("multiselect", problem) for problem in problems]


def get_color_or_bw(carrier: sippy.AnyPhysicalCarrier) -> list[str] | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None
    # TODO: translate coloring types
    return [color.id.split("/")[-1] for color in carrier.coloring_type]


ImageSound = Literal[
    "image",
    "image without sound",
    "sound without image",
    "image with sound",
]


def get_image_sound(entity: sippy.IntellectualEntity) -> ImageSound:
    carrier_rep = get_carrier_representation(entity)

    is_sound_film = entity.type == sippy.EntityClass.sound_film
    is_silent_film = entity.type == sippy.EntityClass.silent_film
    has_missing_audio_reels = carrier_rep.has_missing_audio_reels
    has_missing_image_reels = carrier_rep.has_missing_image_reels

    if has_missing_audio_reels and is_sound_film:
        return "image without sound"
    if has_missing_image_reels and is_sound_film:
        return "sound without image"
    if is_sound_film:
        return "image with sound"
    if is_silent_film:
        return "image"

    raise ValueError()


def get_material_type(carrier: sippy.AnyPhysicalCarrier) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.stock_type


def get_aspect_ratio(carrier: sippy.AnyPhysicalCarrier) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.aspect_ratio


def get_gauge(carrier: sippy.AnyPhysicalCarrier) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.storage_medium.id.split("/")[-1]


def get_brand_of_film_stock(carrier: sippy.AnyPhysicalCarrier) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    if carrier.brand is None:
        return None
    return get_nl_string(carrier.brand.name)


def get_subtitles(carrier: sippy.AnyPhysicalCarrier) -> Literal["Yes", "No"] | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None
    if len(carrier.has_captioning) == 0:
        return "No"
    return "Yes"


def get_language_subtitles(
    carrier: sippy.AnyPhysicalCarrier,
) -> list[tuple[str, str]] | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None

    langs = chain.from_iterable(
        captions.in_language for captions in carrier.has_captioning
    )
    return [("multiselect", lang) for lang in langs]
