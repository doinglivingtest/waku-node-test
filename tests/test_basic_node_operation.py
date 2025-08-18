import pytest
import allure
import time
from config.settings import settings

@allure.epic("Waku Node Testing")
@allure.feature("Basic Node Operations")
@pytest.mark.basic
class TestBasicNodeOperation:
    """Test suite for basic Waku node operations"""

    @allure.story("Node Startup and Info Retrieval")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_node_startup_and_info(self, single_node):
        """Test that a Waku node starts and provides debug information"""
        with allure.step("Verify node is running"):
            assert single_node['container'].status == "running"

        with allure.step("Get node debug information"):
            node_info = single_node['client'].get_node_info()
            assert node_info is not None
            assert 'enrUri' in node_info

            # Store ENR URI for later use
            enr_uri = node_info['enrUri']
            allure.attach(enr_uri, "ENR URI", allure.attachment_type.TEXT)
            assert enr_uri.startswith('enr:')

    @allure.story("Topic Subscription")
    @allure.severity(allure.severity_level.NORMAL)
    def test_topic_subscription(self, single_node):
        """Test subscribing to a relay topic"""
        with allure.step("Subscribe to topic"):
            success = single_node['client'].subscribe_to_topic([settings.DEFAULT_TOPIC])
            assert success, "Failed to subscribe to topic"

    @allure.story("Message Publishing")
    @allure.severity(allure.severity_level.NORMAL)
    def test_message_publishing(self, single_node):
        """Test publishing a message to a topic"""
        # First subscribe to topic
        single_node['client'].subscribe_to_topic([settings.DEFAULT_TOPIC])

        with allure.step("Publish message"):
            success = single_node['client'].publish_message(
                payload=settings.DEFAULT_MESSAGE,
                content_topic=settings.DEFAULT_TOPIC,
                timestamp=int(time.time() * 1000)
            )
            assert success, "Failed to publish message"

    @allure.story("Message Retrieval")
    @allure.severity(allure.severity_level.NORMAL)
    def test_message_retrieval(self, single_node):
        """Test retrieving messages from a topic"""
        # Subscribe and publish message first
        single_node['client'].subscribe_to_topic([settings.DEFAULT_TOPIC])
        single_node['client'].publish_message(
            payload=settings.DEFAULT_MESSAGE,
            content_topic=settings.DEFAULT_TOPIC,
            timestamp=int(time.time() * 1000)
        )

        # Wait a bit for message to be stored
        time.sleep(2)

        with allure.step("Retrieve messages"):
            messages = single_node['client'].get_messages(settings.DEFAULT_TOPIC)
            assert isinstance(messages, list)
            # Note: Messages might be empty if they're not cached
            allure.attach(str(len(messages)), "Number of messages", allure.attachment_type.TEXT)
