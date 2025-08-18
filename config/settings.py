from pydantic_settings import BaseSettings
from typing import Dict, Any
import os

class Settings(BaseSettings):
    """Application settings and configuration"""

    # Docker settings
    DOCKER_IMAGE: str = "wakuorg/nwaku:v0.24.0"
    DOCKER_NETWORK_NAME: str = "waku"
    DOCKER_NETWORK_SUBNET: str = "172.18.0.0/16"
    DOCKER_NETWORK_GATEWAY: str = "172.18.0.1"

    # Node settings
    NODE1_IP: str = "172.18.111.225"
    NODE2_IP: str = "172.18.111.226"

    # Port mappings
    NODE1_PORTS: Dict[str, int] = {
        "rest": 21161,
        "websocket": 21163,
        "tcp": 21162,
        "discv5": 21164,
        "metrics": 21165
    }

    NODE2_PORTS: Dict[str, int] = {
        "rest": 21171,
        "websocket": 21173,
        "tcp": 21172,
        "discv5": 21174,
        "metrics": 21175
    }

    # Test settings
    DEFAULT_TOPIC: str = "/my-app/2/chatroom-1/proto"
    DEFAULT_MESSAGE: str = "UmVsYXkgd29ya3MhIQ=="  # Base64 encoded "Relay works!!"

    # Timeouts
    NODE_STARTUP_TIMEOUT: int = 30
    PEER_CONNECTION_TIMEOUT: int = 60
    MESSAGE_PROPAGATION_TIMEOUT: int = 10

    # API endpoints
    DEBUG_INFO_ENDPOINT: str = "/debug/v1/info"
    SUBSCRIPTIONS_ENDPOINT: str = "/relay/v1/auto/subscriptions"
    MESSAGES_ENDPOINT: str = "/relay/v1/auto/messages"
    PEERS_ENDPOINT: str = "/admin/v1/peers"

    class Config:
        env_file = ".env"

settings = Settings()