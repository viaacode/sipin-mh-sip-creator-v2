from typing import Any
from threading import Thread
from queue import Queue
import json
from time import sleep
from pathlib import Path

from cloudevents.events import EventOutcome
import pytest
import pulsar

from cloudevents import PulsarBinding
from testcontainers.core.container import DockerContainer

from app.app import EventListener

try:
    from transformator.v2_1 import transform_sip
except ImportError:
    raise ImportError(
        "Install the transformator to run the tests: pip install -e './tests/transformator[dev]' --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be --upgrade"
    )


@pytest.fixture
def client(pulsar_config: dict[str, Any]) -> pulsar.Client:
    return pulsar.Client(f"pulsar://{pulsar_config['host']}:{pulsar_config['port']}")


@pytest.fixture
def producer(
    request: pytest.FixtureRequest, client: pulsar.Client, pulsar_config: dict[str, Any]
) -> pulsar.Producer:
    # Pretends to be the transformator service
    producer = client.create_producer(pulsar_config["consumer_topic"])

    def remove_producer():
        producer.close()

    request.addfinalizer(remove_producer)
    return producer


@pytest.fixture
def consumer(
    request: pytest.FixtureRequest, client: pulsar.Client, pulsar_config: dict[str, Any]
) -> pulsar.Consumer:
    # Pretends to be the transport service
    consumer = client.subscribe(pulsar_config["producer_topic"], "test_subscriber")

    def remove_consumer():
        consumer.close()

    request.addfinalizer(remove_consumer)
    return consumer


def test_pulsar_container_running(pulsar_container: DockerContainer):
    exit_code, _ = pulsar_container.exec("pulsar version")
    assert exit_code == 0


def test_event_listener():
    event_listener = EventListener(timeout_ms=500)

    def task():
        sleep(1)
        event_listener.running = False

    thread = Thread(target=task)
    thread.start()
    event_listener.start_listening()
    thread.join()


def test_message(producer: pulsar.Producer, consumer: pulsar.Consumer):
    event_properties = {
        "id": "...",
        "source": "...",
        "specversion": "1.0",
        "type": "...",
        "datacontenttype": "application/json",
        "subject": "...",
        "time": "2022-05-18T16:08:41.356423+00:00",
        "outcome": "success",
        "correlation_id": "...",
        "content_type": "application/cloudevents+json; charset=utf-8",
    }

    event_data = {
        "data": transform_sip(
            Path(
                "tests/sip-examples/2.1/3D_3d4bd7ca-38c6-11ed-95f2-7e92631d7d28/uuid-de61d4af-d19c-4cc7-864d-55573875b438"
            )
        )
        | {"is_valid": "..."}
    }

    event_listener = EventListener(timeout_ms=200)
    queue: Queue[pulsar.Message] = Queue()

    def produce():
        sleep(0.1)
        producer.send(
            json.dumps(event_data).encode("utf-8"),
            properties=event_properties,
        )

    def consume():
        try:
            message = consumer.receive(timeout_millis=5000)
            queue.put(message)
        except pulsar.Timeout:
            pass
        finally:
            event_listener.running = False

    producer_thread = Thread(target=produce)
    consumer_thread = Thread(target=consume)
    consumer_thread.start()
    producer_thread.start()
    event_listener.start_listening()
    producer_thread.join()
    consumer_thread.join()

    message = queue.get_nowait()
    event = PulsarBinding.from_protocol(message)  # type: ignore

    print(event.get_data())

    assert event.outcome == EventOutcome.SUCCESS
    assert "pid" in event.get_data()
