from pathlib import Path

import pytest

import sippy
from app.helpers.template import generate_mets_from_sip


# Install the transformator and its dependencies.
# The current setup is very ugly because the transformator is not a library.
# Furthermore setuptools can't have dependecies defined by a relative path.

# pip install ./transformator --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be --upgrade

try:
    from transformator.v2_1 import transform_sip
except ImportError:
    raise ImportError("Install the transformator to run the tests.")


sip_paths = set(Path("tests/sip-examples/2.1").iterdir())

exclude = [
    "tests/sip-examples/2.1/ftp_sidecar_904c6e86-d36a-4630-897b-bb560ce4b690",
    "tests/sip-examples/2.1/newspaper_tiff_alto_pdf_ebe47259-8f23-4a2d-bf49-55ae1d855393",
    "tests/sip-examples/2.1/newspaper_c44a0b0d-6e2f-4af2-9dab-3a9d447288d0",
    "tests/sip-examples/2.1/subtitles_d3e1a978-3dd8-4b46-9314-d9189a1c94c6",
]

excluded_paths = {Path(p) for p in exclude}

sip_paths = sip_paths - excluded_paths
unzipped_paths = [(next(path.iterdir())) for path in sip_paths]
unzipped_path_names = [str(path.parent.name) for path in unzipped_paths]


@pytest.mark.parametrize("sip_path", unzipped_paths, ids=unzipped_path_names)
def test_examples(sip_path: Path):
    data = transform_sip(sip_path)
    sip = sippy.SIP.deserialize(data)
    generate_mets_from_sip(sip, "test_pid", "disk", "25.1")
