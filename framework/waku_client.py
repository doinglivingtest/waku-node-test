import requests
import logging
import json
from typing import Dict, Any, List, Optional
from urllib.parse import quote
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)

class WakuClient:
    """HTTP client for interacting with Waku node REST API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_node_info(self) -> Dict[str, Any]:
        """Get node debug information"""
        url = f"{self.base_url}{settings.DEBUG_INFO_ENDPOINT}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_enr_uri(self) -> str:
        """Extract ENR URI from node info"""
        node_info = self.get_node_info()
        return node_info.get('enrUri', '')

    def subscribe_to_topic(self, topics: List[str]) -> bool:
        """Subscribe to relay topics"""
        url = f"{self.base_url}{settings.SUBSCRIPTIONS_ENDPOINT}"
        response = self.session.post(url, json=topics)
        response.raise_for_status()
        return response.status_code == 200

    def publish_message(
            self,
            payload: str,
            content_topic: str,
            timestamp: Optional[int] = None
    ) -> bool:
        """Publish a message to a topic"""
        url = f"{self.base_url}{settings.MESSAGES_ENDPOINT}"

        message_data = {
            "payload": payload,
            "contentTopic": content_topic
        }

        if timestamp:
            message_data["timestamp"] = timestamp

        response = self.session.post(url, json=message_data)
        response.raise_for_status()
        return response.status_code == 200

    def get_messages(self, content_topic: str) -> List[Dict[str, Any]]:
        """Retrieve messages for a topic"""
        encoded_topic = quote(content_topic, safe='')
        url = f"{self.base_url}{settings.MESSAGES_ENDPOINT}/{encoded_topic}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=2, min=5, max=30)
    )
    def get_peers(self) -> List[Dict[str, Any]]:
        """Get connected peers"""
        url = f"{self.base_url}{settings.PEERS_ENDPOINT}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def wait_for_peer_connection(self, expected_peer_id: str, timeout: int = 60) -> bool:
        """Wait for a specific peer to be connected"""
        try:
            peers = self.get_peers()
            for peer in peers:
                if expected_peer_id in str(peer):
                    logger.info(f"Peer connection established: {expected_peer_id}")
                    return True
            return False
        except Exception as e:
            logger.warning(f"Error checking peer connection: {e}")
            return False