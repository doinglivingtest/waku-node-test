import pytest
import logging
from framework.docker_manager import DockerManager
from framework.waku_client import WakuClient
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="module")
def docker_manager():
    """Docker manager fixture"""
    manager = DockerManager()
    yield manager
    manager.cleanup()

@pytest.fixture(scope="module")
def waku_network(docker_manager):
    """Create Waku network"""
    return docker_manager.create_network()

@pytest.fixture(scope="class")
def single_node(docker_manager, waku_network):
    """Single Waku node fixture"""
    container = docker_manager.start_waku_node(
        node_name="waku_node_single",
        ports=settings.NODE1_PORTS,
        external_ip=settings.NODE1_IP
    )

    docker_manager.connect_container_to_network(container, settings.NODE1_IP)

    client = WakuClient(f"http://127.0.0.1:{settings.NODE1_PORTS['rest']}")

    yield {
        'container': container,
        'client': client,
        'base_url': f"http://127.0.0.1:{settings.NODE1_PORTS['rest']}"
    }

@pytest.fixture(scope="class")
def two_nodes(docker_manager, waku_network):
    """Two connected Waku nodes fixture"""
    # Start first node
    node1_container = docker_manager.start_waku_node(
        node_name="waku_node1",
        ports=settings.NODE1_PORTS,
        external_ip=settings.NODE1_IP
    )

    docker_manager.connect_container_to_network(node1_container, settings.NODE1_IP)

    node1_client = WakuClient(f"http://127.0.0.1:{settings.NODE1_PORTS['rest']}")

    # Get ENR URI from first node
    enr_uri = node1_client.get_enr_uri()

    # Start second node with bootstrap
    node2_container = docker_manager.start_waku_node(
        node_name="waku_node2",
        ports=settings.NODE2_PORTS,
        external_ip=settings.NODE2_IP,
        bootstrap_node=enr_uri
    )

    docker_manager.connect_container_to_network(node2_container, settings.NODE2_IP)

    node2_client = WakuClient(f"http://127.0.0.1:{settings.NODE2_PORTS['rest']}")

    yield {
        'node1': {
            'container': node1_container,
            'client': node1_client,
            'base_url': f"http://127.0.0.1:{settings.NODE1_PORTS['rest']}"
        },
        'node2': {
            'container': node2_container,
            'client': node2_client,
            'base_url': f"http://127.0.0.1:{settings.NODE2_PORTS['rest']}"
        }
    }