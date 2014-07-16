from common_fixtures import *  # NOQA


def test_sample_data(admin_client, system_account):

    network = find_one(admin_client.list_network, uuid='unmanaged')
    assert network.accountId == system_account.id
    assert network.isPublic
    assert network.kind == 'network'
    assert network.removed is None
    assert network.state == 'active' or network.state == 'inactive'
    assert 'hostVnetUri' not in network
    assert 'dynamicCreateVnet' not in network
    assert 'libvirt' not in network.data

    network = find_one(admin_client.list_network, uuid='managed-docker0')
    assert network.accountId == system_account.id
    assert network.isPublic
    assert network.kind == 'hostOnlyNetwork'
    assert network.removed is None
    assert network.state == 'active' or network.state == 'inactive'
    assert network.hostVnetUri == 'bridge://docker0'
    assert network.dynamicCreateVnet
    assert network.data.libvirt == {
        'network': {
            'source': [
                {
                    'bridge': 'docker0'
                }
            ],
            'type': 'bridge'
        }
    }

    subnet = find_one(network.subnets)

    assert subnet.accountId == system_account.id
    assert subnet.cidrSize == 24
    assert subnet.endAddress == '10.42.0.250'
    assert subnet.gateway == '10.42.0.1'
    assert subnet.isPublic
    assert subnet.kind == 'subnet'
    assert subnet.networkAddress == '10.42.0.0'
    assert subnet.networkId == network.id
    assert subnet.startAddress == '10.42.0.2'
    assert subnet.state == 'active'

    network_service_provider = find_one(network.networkServiceProviders)

    assert network_service_provider.accountId == system_account.id
    assert network_service_provider.kind == 'agentInstanceProvider'
    assert network_service_provider.networkId == network.id
    assert network_service_provider.removed is None
    assert network_service_provider.state == 'active'
    assert network_service_provider.agentInstanceImageUuid is None

    network_services = find_count(7, network.networkServices)
    network_service_kinds = set()

    for service in network_services:
        network_service_kinds.add(service.kind)

        assert service.accountId == system_account.id
        assert service.networkId == network.id
        assert service.networkServiceProviderId == network_service_provider.id
        assert service.removed is None

        if service.kind == 'dhcpService':
            service.uuid = 'docker0-dhcp-service'
        if service.kind == 'dnsService':
            service.uuid = 'docker0-dns-service'
        if service.kind == 'linkService':
            service.uuid = 'docker0-link-service'
        if service.kind == 'ipsecTunnelService':
            service.uuid = 'docker0-ipsec-tunnel-service'
        if service.kind == 'portService':
            service.uuid = 'docker0-port-service'
        if service.kind == 'hostNatGatewayService':
            service.uuid = 'docker0-host-nat-gateway-service'
        if service.kind == 'metadataService':
            service.uuid = 'metadata-service'

    assert network_service_kinds == set(['dnsService',
                                         'dhcpService',
                                         'hostNatGatewayService',
                                         'ipsecTunnelService',
                                         'metadataService',
                                         'portService',
                                         'linkService'])
