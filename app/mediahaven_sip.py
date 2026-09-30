"""
The version-agnostic contract that every SIP version's creator implements.
"""

from pathlib import Path
from typing import Any, Protocol
import shutil
import zipfile

from pydantic import BaseModel

import sippy


class MediahavenSip(BaseModel):
    path: Path
    mets_xml: str
    entity_record_type: str

    @property
    def zip_path(self) -> Path:
        return self.path.with_suffix(".zip")


class MediahavenSipWriter(Protocol):
    def __call__(
        self, sip: sippy.SIP, config: dict[str, Any], pid: str
    ) -> MediahavenSip: ...


def zip_mediahaven_sip(mh_sip: MediahavenSip) -> None:
    with zipfile.ZipFile(mh_sip.zip_path, "w") as zf:
        for path in mh_sip.path.rglob("*"):
            zf.write(path, arcname=path.relative_to(mh_sip.path))


def remove_mediahaven_sip_folder(mh_sip: MediahavenSip) -> None:
    shutil.rmtree(mh_sip.path)
