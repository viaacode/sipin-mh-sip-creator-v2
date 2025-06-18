from datetime import datetime


from sippy.descriptive import (
    ContentPartner,
    Newspaper,
    Organization,
    Person,
    ServiceProvider,
    Thing,
)
from sippy.namespaces import cryptoHash
from sippy.objects import (
    AudioReel,
    CarrierRepresentation,
    Concept,
    DigitalRepresentation,
    File,
    FileFormat,
    Fixity,
    ImageReel,
    IntellectualEntity,
    LocalIdentifier,
    OpenCaptions,
    PhysicalCarrier,
    Place,
    QuantitativeValue,
    Reference,
    Role,
    StorageMedium,
)
from sippy.events import Event
from sippy.sip import EARKNote, METSAgent, METSHdr, PremisAgent
from sippy.utils import (
    DateTime,
    EDTF_level0,
    EDTF_level1,
    Float,
    LangStr,
    NonNegativeInt,
    SHACLError,
    String,
    TimeDelta,
    URIRef,
)
from sippy.vocabulary import ColoringType, EntityClass, Format

metsHdr = METSHdr(
    agents=[
        METSAgent(
            role="CREATOR",
            type="OTHER",
            other_type="SOFTWARE",
            name="meemoo SIP creator",
            note=EARKNote(value="0.1.0", note_type="SOFTWARE VERSION"),
        ),
        METSAgent(
            role="ARCHIVIST",
            type="ORGANIZATION",
            name="archival creator",
            note=EARKNote(value="OR-jw86m54", note_type="IDENTIFICATIONCODE"),
        ),
        METSAgent(
            role="CREATOR",
            type="ORGANIZATION",
            name="submitting organization",
            note=EARKNote(value="OR-183420s", note_type="IDENTIFICATIONCODE"),
        ),
    ]
)

premis_agents = [
    PremisAgent(
        identifier="uuid-ef2f95b3-529a-4226-af41-f103021d8089",
        name="David",
        type="SP-AGENT",
    ),
    PremisAgent(
        identifier="uuid-2cbc112a-84e2-4999-8f49-03156509a784",
        name="David/ScanStation",
        type="SP-AGENT",
    ),
    PremisAgent(
        identifier="uuid-b16df46f-69cb-4899-8f64-7bc77808a11e",
        name="JulienS/Nucoda",
        type="SP-AGENT",
    ),
    PremisAgent(
        identifier="uuid-6e7385e3-97e7-43ea-b6d5-06ba039c2db6",
        name="JulienS/RAWcooked 23.09.20241109, FFmpeg 7.1",
        type="SP-AGENT",
    ),
]

# fix lsp not accessed error
_ = metsHdr
_ = premis_agents

f = IntellectualEntity(
    id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04",
    type=EntityClass.film,
    identifier="kiodik2z9x",
    primary_identifier=[LocalIdentifier(value="2891#422")],
    local_identifier=[],
    maintainer=ContentPartner(
        identifier="OR-jw86m54",
        pref_label=LangStr.codes(nl="archival creator"),
    ),
    # Title
    name=LangStr.codes(nl="Katten in de tuin"),
    is_represented_by=[
        # TODO: Correct mapping
        CarrierRepresentation(
            id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2",
            represents=Reference(id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"),
            is_carrier_copy_of=Reference(
                id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"
            ),
            stored_at=[
                ImageReel(
                    identifier="AFLM_FEL_001392",
                    medium=StorageMedium(
                        id="https://data.hetarchief.be/id/carrier-type/super8mmfilm",
                    ),
                    coloring_type=[
                        Concept(
                            id="https://data.hetarchief.be/id/color-type/BandW"
                        ),
                        Concept(
                            id="https://data.hetarchief.be/id/color-type/Color"
                        ),
                    ],
                    has_captioning=[OpenCaptions(in_language=["nl"])],
                ),
            ],
        ),
        # Representation 1 - mkv master
        DigitalRepresentation(
            id="uuid-5defe23d-23b9-4819-a189-bc4793e7e60b",
            represents=Reference(id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"),
            is_master_copy_of=Reference(
                id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"
            ),
            includes=[
                File(
                    id="uuid-7df1ed59-40dd-4323-83c9-e730615eea34",
                    size=NonNegativeInt(value=6255),
                    fixity=Fixity(
                        type="http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5",
                        value="a427d6f9dcf9d4db5145dc159fef7727",
                    ),
                    is_included_in=[
                        Reference(id="uuid-5defe23d-23b9-4819-a189-bc4793e7e60b")
                    ],
                    format=FileFormat(
                        id="https://www.nationalarchives.gov.uk/pronom/fmt/569"
                    ),
                    original_name="master_dummy.mkv",
                ),
            ],
        ),
        # Representation 2 - mov mezzanine
        DigitalRepresentation(
            id="uuid-ed415625-bc4b-4ecc-b220-9c9d4400bde8",
            represents=Reference(id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"),
            is_mezzanine_copy_of=Reference(
                id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"
            ),
            includes=[
                File(
                    id="uuid-b8e8db68-296b-4025-9dad-df966fe05b70",
                    size=NonNegativeInt(value=52574),
                    fixity=Fixity(
                        type="http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5",
                        value="04c2f9a43c2aa4d6f6975903bad69a67",
                    ),
                    is_included_in=[
                        Reference(id="uuid-ed415625-bc4b-4ecc-b220-9c9d4400bde8")
                    ],
                    format=FileFormat(
                        id="https://www.nationalarchives.gov.uk/pronom/x-fmt/384"
                    ),
                    original_name="mezzanine_dummy.mov",
                ),
            ],
        ),
        # Representation 3 - scan (pdf)
        DigitalRepresentation(
            id="uuid-d55d9a49-ac38-4849-8262-f978d36a3a24",
            represents=Reference(id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"),
            includes=[
                File(
                    id="uuid-9e74d34e-f2ec-483f-b144-47f63307ecbe",
                    size=NonNegativeInt(value=19933),
                    fixity=Fixity(
                        type="http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5",
                        value="b0dfa6f04e6056ecd953a2ad127820e3",
                    ),
                    is_included_in=[
                        Reference(id="uuid-d55d9a49-ac38-4849-8262-f978d36a3a24")
                    ],
                    format=FileFormat(
                        id="https://www.nationalarchives.gov.uk/pronom/fmt/18"
                    ),
                    original_name="dummy.pdf",
                ),
            ],
        ),
        # Representation 4 - scan (jpg)
        DigitalRepresentation(
            id="uuid-e2be2807-ba06-45a9-890d-4d275145aa9e",
            represents=Reference(id="uuid-f9ef158c-f03c-4840-836e-8ffb8e8ebe04"),
            includes=[
                File(
                    id="uuid-75d336db-603d-4795-b6cc-30bd7c583f8c",
                    size=NonNegativeInt(value=5913),
                    fixity=Fixity(
                        type="http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5",
                        value="b14d633a01600edabc450a0d0ae4390d",
                    ),
                    is_included_in=[
                        Reference(id="uuid-e2be2807-ba06-45a9-890d-4d275145aa9e")
                    ],
                    format=FileFormat(
                        id="https://www.nationalarchives.gov.uk/pronom/fmt/43"
                    ),
                    original_name="dummy.jpg",
                ),
            ],
        ),
    ],
    format=String(value=Format.film),
    keywords=[
        LangStr.codes(nl="amateur recording"),
    ],
    creator=[
        Role(
            role_name="archiefvormer",
            creator=Thing(name=LangStr.codes(nl="Dummy privéarchief")),
        )
    ],
    date_created=EDTF_level0(value="XXXX-XX-XX"),
    copyright_holder=[Thing(name=LangStr.codes(nl="© dummyorganisatie"))],
    description=LangStr.codes(nl="Katten ravotten in de tuin"),
    alternative_name=[LangStr.codes(nl="Ons katten in den hof")],
    license=[
        Concept(id=uri)
        for uri in [
            "https://data.hetarchief.be/id/license/VIAA-ONDERWIJS",
            "https://data.hetarchief.be/id/license/VIAA-ONDERZOEK",
            "https://data.hetarchief.be/id/license/VIAA-INTRA-CP-CONTENT",
            "https://data.hetarchief.be/id/license/VIAA-INTRA_CP-METADATA-ALL",
            "https://data.hetarchief.be/id/license/VIAA-PUBLIEK-METADATA-LTD",
            "https://data.hetarchief.be/id/license/BEZOEKERTOOL-CONTENT",
            "https://data.hetarchief.be/id/license/BEZOEKERTOOL-METADATA-ALL",
        ]
    ],
    # Refs
    has_master_copy=[Reference(id="uuid-5defe23d-23b9-4819-a189-bc4793e7e60b")],
    has_mezzanine_copy=[Reference(id="uuid-ed415625-bc4b-4ecc-b220-9c9d4400bde8")],
    has_carrier_copy=Reference(id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2"),
)
events = [
    # Registration
    Event(
        id="uuid-e435a1eb-fa72-4221-b673-3cc9289d0904",
        type="https://data.hetarchief.be/id/event-type/registration",
        started_at_time=DateTime(value=datetime(2021, 4, 2, 9, 4, 4)),
        ended_at_time=DateTime(value=datetime(2021, 4, 2, 9, 4, 4)),
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        implemented_by=ContentPartner(
            identifier="OR-1111111",
            pref_label=LangStr.codes(nl="CP-name"),
        ),
        source=[
            Reference(id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2"),
        ],
    ),
    # Checkout
    Event(
        id="uuid-54c8c6f6-2981-41fd-bd02-edcb6e5b8871",
        type="https://data.hetarchief.be/id/event-type/check-out",
        started_at_time=DateTime(value=datetime(2021, 12, 28, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2021, 12, 28, 0, 0, 0)),
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        source=[Reference(id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2")],
    ),
    # Inspection
    Event(
        id="uuid-02411acf-e14f-49bb-9beb-f675dc2b351e",
        type="https://data.hetarchief.be/id/event-type/inspection",
        started_at_time=DateTime(value=datetime(2022, 3, 25, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2022, 3, 25, 0, 0, 0)),
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        outcome_note="CEX / COLOR / MUTE",
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        source=[Reference(id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2")],
        was_associated_with=[Person(name=LangStr.codes(nl="David"))],
    ),
    # Digitization
    Event(
        id="uuid-652dd33d-367b-4a55-8e02-14f3e304d853",
        type="https://data.hetarchief.be/id/event-type/digitization",
        started_at_time=DateTime(value=datetime(2022, 4, 26, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2022, 4, 26, 0, 0, 0)),
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        outcome_note="Abrasion marks, scratches, inlaid dust/dirt, important grain, apparent vignetting, slight instability, under/overexposure related to camera capture, slightly overscanned because of image between perfs or changing framing, dirty camera gate on some scenes",
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        source=[Reference(id="uuid-eb2175c9-56f9-4e7e-9192-0a11a297c1e2")],
        was_associated_with=[Person(name=LangStr.codes(nl="David/ScanStation"))],
        result=[Reference(id="uuid-93199782-ab90-4ec4-ae43-92eb708a151d")],
    ),
    # Compression
    Event(
        id="uuid-ddcd47c0-1967-475d-a3d4-e1d7fcc98729",
        type="https://data.hetarchief.be/id/event-type/compression",
        started_at_time=DateTime(value=datetime(2022, 4, 28, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2022, 4, 28, 0, 0, 0)),
        note="RAWcooked 23.09.20241109, FFmpeg 7.1\n\tParameters used: --all -o Variation_Examples/AIP_VARIATION_3-M_image_0_sound_N_scans/rawcooked/t14th8df5w_001.mkv\n\tPackage name: t14th8df5w_001_%06d.dpx\n\tTrack 1:\n\t(000001 --> 000025)\n\tDPX/Raw/RGB/8bit/U/LE\n\tInfo: Reversibility data created by RAWcooked 23.09.20241109.\n\tInfo: Uncompressed file hashes (used by reversibility check) present.\n\tInfo: Reversibility was checked, no issue detected.",
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        source=[Reference(id="uuid-93199782-ab90-4ec4-ae43-92eb708a151d")],
        was_associated_with=[
            Person(
                name=LangStr.codes(
                    nl="JulienS/RAWcooked 23.09.20241109, FFmpeg 7.1<"
                )
            )
        ],
        result=[Reference(id="uuid-ed415625-bc4b-4ecc-b220-9c9d4400bde8")],
    ),
    # Editing
    Event(
        id="uuid-de489f24-98d1-4032-b39c-2f36e1cfcc63",
        type="https://data.hetarchief.be/id/event-type/editing",
        started_at_time=DateTime(value=datetime(2022, 4, 28, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2022, 4, 28, 0, 0, 0)),
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        outcome_note="Abrasion marks, scratches, inlaid dust/dirt, important grain, slight instability, under/overexposure related to camera capture, slight color fading/shift on some scenes. MUTE . Speed 16 fps. MIX COLOR/BW.",
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        was_associated_with=[Person(name=LangStr.codes(nl="JulienS/Nucoda<"))],
        source=[Reference(id="uuid-5defe23d-23b9-4819-a189-bc4793e7e60b")],
        result=[Reference(id="uuid-ed415625-bc4b-4ecc-b220-9c9d4400bde8")],
    ),
    # Transfer
    Event(
        id="uuid-019a16cf-9d35-469d-8c14-a8ed1564003d",
        type="https://data.hetarchief.be/id/event-type/transfer",
        started_at_time=DateTime(value=datetime(2022, 5, 7, 0, 0, 0)),
        ended_at_time=DateTime(value=datetime(2022, 5, 7, 0, 0, 0)),
        event_detail_extension={"lto_id": "I61842L6"},
        outcome=URIRef(
            id="http://id.loc.gov/vocabulary/preservation/eventOutcome/suc"
        ),
        implemented_by=ServiceProvider(
            identifier="OR-2222222",
            pref_label=LangStr.codes(nl="SP-name"),
        ),
        source=[Reference(id="uuid-5defe23d-23b9-4819-a189-bc4793e7e60b")],
    ),
]


digi_reps = [
    repr for repr in f.is_represented_by if isinstance(repr, DigitalRepresentation)
]

print(f"Found {len(digi_reps)} digital representations.")
