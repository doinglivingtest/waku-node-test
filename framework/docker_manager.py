import docker
import logging
import time
from typing import Optional, Dict, Any, List
from docker.models.containers import Container
from docker.models.networks import Network
from config.settings import settings

logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker containers and networks for Waku nodes"""

    def __init__(self):
        self.client = docker.from_env()
        self.containers: List[Container] = []
        self.network: Optional[Network] = None

    def _wait_for_ports_available(self, ports: Dict[str, int], max_attempts: int = 30):
        """Wait for ports to become available"""
        import socket
        import time

        for attempt in range(max_attempts):
            all_available = True

            for port_name, port_num in ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    # Try to bind to the port
                    sock.bind(('127.0.0.1', port_num))
                    sock.close()
                except socket.error:
                    logger.info(f"Port {port_num} ({port_name}) still in use, waiting...")
                    all_available = False
                    break
                finally:
                    try:
                        sock.close()
                    except:
                        pass

            if all_available:
                logger.info("All ports are now available")
                return True

            time.sleep(2)

        logger.error(f"Ports still not available after {max_attempts * 2} seconds")
        return False

    def create_network(self) -> Network:
        """Create Docker network for Waku nodes"""
        try:
            # Remove existing network if exists
            try:
                existing_network = self.client.networks.get(settings.DOCKER_NETWORK_NAME)
                existing_network.remove()
                logger.info(f"Removed existing network: {settings.DOCKER_NETWORK_NAME}")
            except docker.errors.NotFound:
                pass

            # Create new network
            ipam_pool = docker.types.IPAMPool(
                subnet=settings.DOCKER_NETWORK_SUBNET,
                gateway=settings.DOCKER_NETWORK_GATEWAY
            )
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

            self.network = self.client.networks.create(
                name=settings.DOCKER_NETWORK_NAME,
                driver="bridge",
                ipam=ipam_config
            )
            logger.info(f"Created network: {settings.DOCKER_NETWORK_NAME}")
            return self.network

        except Exception as e:
            logger.error(f"Failed to create network: {e}")
            raise

    def start_waku_node(
            self,
            node_name: str,
            ports: Dict[str, int],
            external_ip: str,
            bootstrap_node: Optional[str] = None
    ) -> Container:
        """Start a Waku node container"""

        # First, ensure ports are available
        if not self._wait_for_ports_available(ports):
            raise RuntimeError(f"Required ports for {node_name} are not available")

        # Remove any existing container with the same name
        try:
            existing_container = self.client.containers.get(node_name)
            existing_container.stop(timeout=10)
            existing_container.remove()
            logger.info(f"Removed existing container: {node_name}")
            # Wait a bit after removal
            time.sleep(3)
        except docker.errors.NotFound:
            pass  # Container doesn't exist, which is fine

        # Base command arguments
        cmd_args = [
            f"--listen-address=0.0.0.0",
            f"--rest=true",
            f"--rest-admin=true",
            f"--websocket-support=true",
            f"--log-level=TRACE",
            f"--rest-relay-cache-capacity=100",
            f"--websocket-port={ports['websocket']}",
            f"--rest-port={ports['rest']}",
            f"--tcp-port={ports['tcp']}",
            f"--discv5-udp-port={ports['discv5']}",
            f"--rest-address=0.0.0.0",
            f"--nat=extip:{external_ip}",
            f"--peer-exchange=true",
            f"--discv5-discovery=true",
            f"--relay=true"
        ]

        # Add bootstrap node if provided
        if bootstrap_node:
            cmd_args.append(f"--discv5-bootstrap-node={bootstrap_node}")

        # Port mappings
        port_mappings = {
            f"{ports['rest']}/tcp": ports['rest'],
            f"{ports['websocket']}/tcp": ports['websocket'],
            f"{ports['tcp']}/tcp": ports['tcp'],
            f"{ports['discv5']}/udp": ports['discv5'],
            f"{ports['metrics']}/tcp": ports['metrics']
        }

        try:
            container = self.client.containers.run(
                image=settings.DOCKER_IMAGE,
                command=cmd_args,
                name=node_name,
                ports=port_mappings,
                detach=True,
                remove=False,
            )

            self.containers.append(container)
            logger.info(f"Started container: {node_name}")

            # Wait for container to be ready
            self._wait_for_container_ready(container)

            return container

        except Exception as e:
            logger.error(f"Failed to start container {node_name}: {e}")
            raise

    def connect_container_to_network(self, container: Container, ip_address: str):
        """Connect container to the Waku network"""
        if not self.network:
            raise RuntimeError("Network not created")

        try:
            self.network.connect(container, ipv4_address=ip_address)
            logger.info(f"Connected {container.name} to network with IP: {ip_address}")
        except Exception as e:
            logger.error(f"Failed to connect container to network: {e}")
            raise

    def _wait_for_container_ready(self, container: Container, timeout: int = 30):
        """Wait for container to be in running state"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            container.reload()
            if container.status == "running":
                # Additional wait for service to be ready
                time.sleep(5)
                return
            time.sleep(1)

        raise TimeoutError(f"Container {container.name} not ready within {timeout} seconds")

    def cleanup(self):
        """Clean up containers and network"""
        # Stop and remove containers
        for container in self.containers:
            try:
                container.stop(timeout=10)
                container.remove()
                logger.info(f"Cleaned up container: {container.name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup container {container.name}: {e}")

        # Remove network
        if self.network:
            try:
                self.network.remove()
                logger.info(f"Cleaned up network: {settings.DOCKER_NETWORK_NAME}")
            except Exception as e:
                logger.warning(f"Failed to cleanup network: {e}")

        self.containers.clear()
        self.network = None