from pit8c.brokers import freedom24
from pit8c.brokers.base import BrokerAdapter, SupportedBroker
from pit8c.exceptions import Pit8cError


def get_broker_adapter(broker: SupportedBroker) -> BrokerAdapter:
    """Return the adapter implementation for the given broker enum."""

    match broker:
        case SupportedBroker.freedom24:
            return freedom24.Freedom24Adapter()
        case _:
            raise Pit8cError(f"Broker '{broker}' not supported yet")
