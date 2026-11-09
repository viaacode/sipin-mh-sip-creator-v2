from pathlib import Path

import pytest

import sippy
from app.v2_1.creator import create_mh_mets_data, create_mh_sidecar_data

from transformator.v2_1 import transform
from transformator.v2_1.mets.mets import OtherContentInformationType


examples = Path("tests/sip-examples/2.1")
newspapers = [
    "newspaper_c44a0b0d-6e2f-4af2-9dab-3a9d447288d0",
    "newspaper_tiff_alto_pdf_ebe47259-8f23-4a2d-bf49-55ae1d855393",
]


@pytest.fixture(autouse=True)
def accept_bibliographic(monkeypatch):
    """
    The transformator rejects bibliographic SIPs until its MODS mapping is done.
    """
    monkeypatch.setattr(
        transform,
        "SUPPORTED_PROFILES",
        [*transform.SUPPORTED_PROFILES, OtherContentInformationType.BIBLIOGRAPHIC],
    )


def load_sip(name: str) -> sippy.SIP:
    sip_path = next((examples / name).iterdir())
    return sippy.SIP.deserialize(transform.transform_sip(sip_path))


@pytest.fixture(params=newspapers)
def sip(request) -> sippy.SIP:
    return load_sip(request.param)


def test_sidecar_type_viaa(sip: sippy.SIP):
    sidecar = create_mh_sidecar_data(sip)

    assert sidecar["Dynamic"]["type_viaa"] == "newspaper"


def test_sidecar_keeps_common_fields(sip: sippy.SIP):
    sidecar = create_mh_sidecar_data(sip)

    assert sidecar["Descriptive"]["mh:Title"]
    assert sidecar["Dynamic"]["dcterms_created"] == sip.entity.date_created.value
    assert sidecar["Dynamic"]["ContentCategory"] == "Textual works – Print"


def test_newspaper_sidecar():
    sidecar = create_mh_sidecar_data(load_sip(newspapers[0]))

    assert sidecar["Descriptive"]["mh:Title"] == "Le Chat Blanc"
    assert sidecar["Dynamic"]["dc_types"] == [
        ("multiselect", "krant"),
        ("multiselect", "amateurkrant"),
    ]
    assert ("Trefwoord", "katten") in sidecar["Dynamic"]["dc_subjects"]
    assert sidecar["Dynamic"]["dcterms_created"] == "XXXX"
    assert sidecar["Dynamic"]["dcterms_issued"] == "2022-08-02"
    assert sidecar["Dynamic"]["dc_rights_licenses"] == [
        ("multiselect", "VIAA-PUBLIEK-METADATA-LTD")
    ]
    assert sidecar["Dynamic"]["dc_coverages"] == [("ruimte", "Gent, België")]
    assert sidecar["Dynamic"]["dc_identifier_localid"] == "CHATBLANC_2022_001"


def test_mets_not_implemented(sip: sippy.SIP):
    with pytest.raises(NotImplementedError, match="no struct map"):
        create_mh_mets_data(sip, sip.entity.identifier, "Disk", "25.1")
