from typing import Any, Literal
from itertools import chain

import sippy


from . import common
from . import helpers

from .common import get_nl_string


def get_mh_mapping(sip: sippy.SIP) -> dict[str, Any]:
    carrier_rep = get_carrier_representation(sip.entity)
    first_physical_carrier = get_first_physical_carrier(carrier_rep)
    common_fields = common.get_mh_mapping(sip)

    fields = {
        "Dynamic": {
            #
            # Carrier representation
            "num_reels": get_number_of_reels(carrier_rep),
            #
            # Intellectual entity
            "type_viaa": sip.entity.format.value,
            "image_sound": get_image_sound(sip.entity),
            #
            # Physical carrier
            "preservation_problems": get_preservation_problems(first_physical_carrier),
            "film_base": get_film_base(first_physical_carrier),
            "dc_description_cast": get_cast(sip.entity),
            "subtitles": get_subtitles(first_physical_carrier),
            "language_subtitles": get_language_subtitles(first_physical_carrier),
            "original_location": get_original_location(first_physical_carrier),
            "format": get_medium(first_physical_carrier),
            "carrier_barcode": get_carrier_barcode(first_physical_carrier),
            "original_carrier_id": common.get_dc_identifier_localid(sip.entity),
            "date": sip.entity.date_created.value,
            #
            # Image and audio reels
            "gauge": get_medium(first_physical_carrier),
            "material_type": get_material_type(first_physical_carrier),
            "aspect_ratio": get_aspect_ratio(first_physical_carrier),
            "brand_of_film_stock": get_brand_of_film_stock(first_physical_carrier),
            #
            # Image Reel
            "color_or_bw": get_color_or_bw(first_physical_carrier),
            "barcode_image_reels": get_barcode_image_reels(carrier_rep),
            "barcode_sound_reels": get_barcode_audio_reels(carrier_rep),
            "batch_pickup_date": common.get_event_date(
                sip, "https://data.hetarchief.be/id/event-type/check-out"
            ),
        },
    }

    return helpers.deepmerge(fields, common_fields)


def get_original_location(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if carrier is None:
        return None

    return carrier.file_path


def get_carrier_barcode(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if carrier is None:
        return None

    return carrier.identifier


def get_film_base(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if carrier is None:
        return carrier
    return carrier.material


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


def get_first_physical_carrier(
    carrier_rep: sippy.CarrierRepresentation,
) -> sippy.AnyPhysicalCarrier | None:
    return next(iter(carrier_rep.stored_at), None)


def get_number_of_reels(rep: sippy.CarrierRepresentation) -> int | None:
    return rep.number_of_reels.value if rep.number_of_reels else None


def get_preservation_problems(
    carrier: sippy.AnyPhysicalCarrier | None,
) -> list[tuple[str, str]] | None:
    if carrier is None:
        return None

    problems = [get_nl_string(prob.pref_label) for prob in carrier.preservation_problem]
    return [("multiselect", problem) for problem in problems]


def get_color_or_bw(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None
    coloring_types = [color.id.split("/")[-1] for color in carrier.coloring_type]
    coloring_types = sorted(coloring_types)
    match coloring_types:
        case ["BandW"]:
            return "Zwart/wit"
        case ["Color"]:
            return "Kleur"
        case ["BandW", "Color"]:
            return "Zwart/wit En Kleur"
        case ["UnknownColorType"]:
            return "Andere"

    return None


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


def get_material_type(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.stock_type


def get_aspect_ratio(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.aspect_ratio


def get_medium(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    return carrier.storage_medium.id.split("/")[-1]


def get_brand_of_film_stock(carrier: sippy.AnyPhysicalCarrier | None) -> str | None:
    if not isinstance(carrier, (sippy.ImageReel, sippy.AudioReel)):
        return None
    if carrier.brand is None:
        return None
    return get_nl_string(carrier.brand.name)


def get_subtitles(
    carrier: sippy.AnyPhysicalCarrier | None,
) -> Literal["Yes", "No"] | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None
    if len(carrier.has_captioning) == 0:
        return "No"
    return "Yes"


def get_language_subtitles(
    carrier: sippy.AnyPhysicalCarrier | None,
) -> list[tuple[str, str]] | None:
    if not isinstance(carrier, sippy.ImageReel):
        return None

    langs = chain.from_iterable(
        captions.in_language for captions in carrier.has_captioning
    )
    return [("multiselect", lang) for lang in langs]


def get_barcode_image_reels(carrier: sippy.CarrierRepresentation) -> str:
    image_reels = [
        reel for reel in carrier.stored_at if isinstance(reel, sippy.ImageReel)
    ]
    ids = [reel.identifier for reel in image_reels]
    return " | ".join(ids)


def get_barcode_audio_reels(carrier: sippy.CarrierRepresentation) -> str:
    image_reels = [
        reel for reel in carrier.stored_at if isinstance(reel, sippy.AudioReel)
    ]
    ids = [reel.identifier for reel in image_reels]
    return " | ".join(ids)


def get_cast(entity: sippy.IntellectualEntity) -> str | None:
    return entity.castmembers
