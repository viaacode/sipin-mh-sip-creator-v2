from pathlib import Path
from typing import Any

import pytest

import sippy
from app.mediahaven_sip import zip_mediahaven_sip
from app.utils import get_mets_creator, get_mediahaven_sip_writer


"""
Since the transformator is not a library and setuptools doesn't support relative paths to packages,
you must install the transformator manually
"""


try:
    from transformator.v2_1 import transform_sip
except ImportError:
    raise ImportError(
        "Install the transformator to run the tests: pip install -e './tests/transformator[dev]' --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be --upgrade"
    )


sip_paths = set(Path("tests/sip-examples/2.1").iterdir())

exclude = [
    "tests/sip-examples/2.1/ftp_sidecar_904c6e86-d36a-4630-897b-bb560ce4b690",
    "tests/sip-examples/2.1/newspaper_tiff_alto_pdf_ebe47259-8f23-4a2d-bf49-55ae1d855393",
    "tests/sip-examples/2.1/newspaper_c44a0b0d-6e2f-4af2-9dab-3a9d447288d0",
    "tests/sip-examples/2.1/subtitles_d3e1a978-3dd8-4b46-9314-d9189a1c94c6",
]

excluded_paths = {Path(p) for p in exclude}

sip_paths = sip_paths - excluded_paths
sip_paths = [(next(path.iterdir())) for path in sip_paths]
sip_path_names = [str(path.parent.name) for path in sip_paths]


@pytest.fixture
def config():
    return {
        "aip_folder": "tests/output/",
        "mh_sidecar_version": "25.1",
        "storage": {
            "default_archive_location": "Disk",
            "tape_content_partners": "",
            "disk_content_partners": "",
        },
    }


@pytest.mark.parametrize("sip_path", sip_paths, ids=sip_path_names)
def test_generate_mediahaven_mets(sip_path: Path):
    data = transform_sip(sip_path)
    sip = sippy.SIP.deserialize(data)

    mets_creator_fn = get_mets_creator(sip)
    mets = mets_creator_fn(sip, sip.entity.identifier, "Disk", "25.1")
    print(mets)


@pytest.mark.parametrize("sip_path", sip_paths, ids=sip_path_names)
def test_create_mediahave_sip(sip_path: Path, config: dict[str, Any]):
    data = transform_sip(sip_path)
    sip = sippy.SIP.deserialize(data)

    # Unlike create_mediahaven_sip, keep the unzipped folder for inspection
    write_mediahaven_sip = get_mediahaven_sip_writer(sip)
    mh_sip = write_mediahaven_sip(sip, config, sip.entity.identifier)
    zip_mediahaven_sip(mh_sip)
