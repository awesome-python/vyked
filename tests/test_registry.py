from unittest import mock
# from vyked.registry import Registry, Repository
from vyked.packet import ControlPacket
import uuid


def service_registered_successfully(registry, *services):
    for service in services:
        service_entry = (
            service['host'], service['port'], service['node_id'], service['type'])
        try:
            entry = registry._repository._registered_services[
                service['service']][service['version']]
            assert service_entry in entry
        except KeyError:
            raise
    return True


def no_pending_services(registry):
    return len(registry._repository.get_pending_services()) == 0


def instance_returned_successfully(response, service):
    instance = (
        service['host'], service['port'], service['node_id'], service['type'])
    for returned_instance in response['params']['instances']:
        t = (
            returned_instance['host'], returned_instance['port'], returned_instance['node'], returned_instance['type'])
        if instance == t:
            return True

    return False


def test_register_independent_service(registry, service_a1):

    registry.register_service(
        packet={'params': service_a1}, registry_protocol=mock.Mock())

    assert service_registered_successfully(registry, service_a1)
    assert no_pending_services(registry)


def test_register_dependent_service(registry, service_a1, service_b1):

    registry.register_service(
        packet={'params': service_b1}, registry_protocol=mock.Mock())
    assert not no_pending_services(registry)

    registry.register_service(
        packet={'params': service_a1}, registry_protocol=mock.Mock())
    assert no_pending_services(registry)

    assert service_registered_successfully(registry, service_a1, service_b1)


def test_deregister_dependent_service(service_a1, service_b1, registry):
    registry.register_service(
        packet={'params': service_b1}, registry_protocol=mock.Mock())
    registry.register_service(
        packet={'params': service_a1}, registry_protocol=mock.Mock())

    assert no_pending_services(registry)

    registry.deregister_service(service_a1['node_id'])
    assert not no_pending_services(registry)


def test_get_instances(service_a1, registry):
    registry.register_service(
        packet={'params': service_a1}, registry_protocol=mock.Mock())

    protocol = mock.Mock()
    registry.get_service_instances(
        packet={'params': service_a1, 'request_id': uuid.uuid4()}, registry_protocol=protocol)

    assert instance_returned_successfully(
        protocol.send.call_args_list[0][0][0], service_a1)


