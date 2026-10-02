from pathlib import Path

from pulsar.exceptions import Timeout

from cloudevents.events import Event, PulsarBinding, EventOutcome, EventAttributes
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services.pulsar import PulsarClient
from app.services.pid import PidClient
from app.utils import create_mediahaven_sip

import sippy


APP_NAME = "sipin-mh-sip-creator-v2"


class EventListener:
    """
    EventListener is responsible for listening to Pulsar events and processing them.
    """

    def __init__(self, timeout_ms: int | None = None):
        """
        Initializes the EventListener with configuration, logging, and Pulsar client.
        """
        config_parser = ConfigParser()
        self.config = config_parser.app_cfg

        self.log = logging.get_logger(__name__, config=config_parser)
        self.pulsar_client = PulsarClient(timeout_ms=timeout_ms)
        self.pid_client = PidClient()

        self.running = True

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
        unzipped_path = event_attributes.get("subject")
        if unzipped_path is None:
            self.log.error("Invalid event: subject is missing.")
            return
        self.log.info(f"Start handling of {unzipped_path}.")
        zip_folder_path = Path(unzipped_path).parent

        event_data = event.get_data()
        event_data.pop("is_valid")
        sip = sippy.SIP.deserialize(event_data)
        pid = self.get_pid(sip)

        mh_sip = create_mediahaven_sip(sip, self.config, pid)

        # Send event on topic
        data = {
            "source": str(zip_folder_path),
            "host": self.config["host"],
            "paths": [
                str(mh_sip.zip_path),
            ],
            "cp_id": sip.entity.maintainer.identifier,
            "type": "complex",
            # Despite the name, this is the MediaHaven record type
            "sip_profile": mh_sip.entity_record_type,
            "pid": pid,
            "outcome": EventOutcome.SUCCESS,
            "metadata": mh_sip.mets_xml,
            "message": f"AIP created: MH2.0 complex created for {unzipped_path}",
        }
        producer_topic = self.config["pulsar"]["producer_topic"]

        self.log.info(data["message"], pid=pid)
        self.produce_event(
            producer_topic,
            data,
            unzipped_path,
            EventOutcome.SUCCESS,
            event.correlation_id,
        )

    def get_pid(self, sip: sippy.SIP) -> str:
        if len(sip.entity.identifier) == 10:
            return sip.entity.identifier
        return self.pid_client.get_pid()

    def start_listening(self):
        """
        Starts listening for incoming messages from the Pulsar topic.
        """
        while self.running:
            try:
                msg = self.pulsar_client.receive()
            except Timeout:
                continue

            try:
                event = PulsarBinding.from_protocol(msg)  # type: ignore
                self.handle_incoming_message(event)
                self.pulsar_client.acknowledge(msg)
            except Exception as e:
                # Catch and log any errors during message processing
                self.log.error(f"Error: {e}")
                self.pulsar_client.negative_acknowledge(msg)

        self.pulsar_client.close()
