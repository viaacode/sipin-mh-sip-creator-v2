from cloudevents.events import Event, PulsarBinding, EventOutcome, EventAttributes
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services.pulsar import PulsarClient
from app.services.pid import PidClient

import os
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader

from app.helpers.template import generate_mets_from_sip

from app.helpers.dummy_sip import f


APP_NAME = "sipin-mh-sip-creator-v2"


class EventListener:
    """
    EventListener is responsible for listening to Pulsar events and processing them.
    """

    def __init__(self):
        """
        Initializes the EventListener with configuration, logging, and Pulsar client.
        """
        config_parser = ConfigParser()
        self.config = config_parser.app_cfg

        self.log = logging.get_logger(__name__, config=config_parser)
        self.pulsar_client = PulsarClient()
        self.pid_client = PidClient()

        self.app_config = self.config["mh-sip-creator"]
        
    def produce_event(
        self,
        topic: str,
        data: dict,
        subject: str,
        outcome: EventOutcome,
        correlation_id: str,
    ):
        """Produce an event on a Pulsar topic.
        Args:
            topic: The topic to send the cloudevent to.
            data: The data payload.
            subject: The subject of the event.
            outcome: The attributes outcome of the Event.
            correlation_id: The correlation ID.
        """
        attributes = EventAttributes(
            type=topic,
            source=APP_NAME,
            subject=subject,
            correlation_id=correlation_id,
            outcome=outcome,
        )

        event = Event(attributes, data)
        self.pulsar_client.produce_event(topic, event)

    def handle_incoming_message(self, event: Event):
        """
        Handles an incoming Pulsar event.

        Args:
            event (Event): The incoming event to process.
        """
        if not event.has_successful_outcome():
            self.log.info(f"Dropping non successful event: {event.get_data()}")
            return

        event_attributes = event.get_attributes()
        
        # Subject contains the path to the unzipped bag
        subject = event_attributes.get("subject")
        if subject is None:
            self.log.error("Invalid event: subject is missing.")
            return
        self.log.info(f"Start handling of {subject}.")
        
        event_data = event.get_data()
        
        sip_metadata = event_data["metadata"]
        
        # todo: deserialize sip_metadata to a real SIP.py object
        # For now, we will use a dummy SIP object for testing purposes
        # json_ld_graph = json.loads(graph_string)["@graph"]

        # for model, model_dict in zip(models, json_ld_graph):
        #     deserialized = model.__class__.model_validate(model_dict)
        
        sip = f
        
        pid = self.pid_client.get_pid()

        files_path = Path(self.app_config["aip_folder"], pid)
        files_path.mkdir(parents=True, exist_ok=True)

        for i in range(len(sip.representations)):
            shutil.copytree(
                Path(subject, f"data/representations/representation_{i+1}/data"),
                Path(files_path, f"representation_{i+1}"),
                copy_function=shutil.move,
            )

        mets_xml = generate_mets_from_sip(sip, pid)

        try:
            # Save the generated XML to a file
            mets_file_path = files_path / "mets.xml"
            with open(mets_file_path, "w") as mets_file:
                mets_file.write(mets_xml)

            self.log.info(f"Generated METS XML file at {mets_file_path}")
        except Exception as e:
            self.log.error(f"Failed to generate METS XML: {e}")
            
        with zipfile.ZipFile(str(Path(f"{files_path}.zip")), "w") as zf:
            for file_path in files_path.rglob("*"):
                zf.write(file_path, arcname=file_path.relative_to(files_path))
        # Remove files folder
        shutil.rmtree(files_path)
            
        # Send event on topic
        data = {
            "source": files_path,
            "host": self.config["host"],
            "paths": [
                str(Path(f"{files_path}.zip")),
            ],
            "cp_id": sip.maintainer.identifier,
            "type": "complex",
            "sip_profile": str(sip.type).lstrip("EntityClass."),
            "pid": pid,
            "outcome": EventOutcome.SUCCESS,
            "metadata": mets_xml,
            "message": f"AIP created: MH2.0 complex created for {event_attributes.get("subject")}",
        }
        producer_topic = self.app_config["producer_topic_complex"]

        self.log.info(data["message"], pid=pid)
        self.produce_event(
            producer_topic, data, subject, EventOutcome.SUCCESS, event.correlation_id
        )

    def start_listening(self):
        """
        Starts listening for incoming messages from the Pulsar topic.
        """
        while True:
            msg = self.pulsar_client.receive()
            try:
                event = PulsarBinding.from_protocol(msg)  # type: ignore
                self.handle_incoming_message(event)
                self.pulsar_client.acknowledge(msg)
            except Exception as e:
                # Catch and log any errors during message processing
                self.log.error(f"Error: {e}")
                self.pulsar_client.negative_acknowledge(msg)

        self.pulsar_client.close()
