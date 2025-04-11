import pytest
from unittest.mock import patch, MagicMock
from api.services.topics_service import extract_topics

@pytest.fixture
def mock_config():
    with patch("api.services.topics_service.Config") as mock_config:
        mock_config.LLM_WRAPPER = "openai"
        mock_config.LLM_MODEL = "gpt-3.5-turbo"
        mock_config.OPENAI_API_KEY = "test-api-key"
        yield mock_config

@pytest.fixture
def mock_logger():
    with patch("api.services.topics_service.logger") as mock_logger:
        yield mock_logger

@pytest.fixture
def mock_model():
    with patch("api.services.topics_service.ChatOpenAI") as mock_openai_model:
        mock_instance = MagicMock()
        mock_openai_model.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_topic_response():
    with patch("api.services.topics_service.TopicResponse") as mock_response:
        yield mock_response

def test_extract_topics_success(mock_config, mock_logger, mock_model, mock_topic_response):
    # Arrange
    transcript = "This is a sample transcript."
    language = "en"
    keyframes_descriptions = ["Keyframe 1 description", "Keyframe 2 description"]
    mock_result = MagicMock()
    mock_result.topics = ["Topic 1", "Topic 2"]
    mock_model.with_structured_output.return_value.invoke.return_value = mock_result

    # Act
    topics = extract_topics(transcript, language, keyframes_descriptions)

    # Assert
    assert topics == ["Topic 1", "Topic 2"]
    mock_logger.info.assert_called()
    mock_logger.debug.assert_called()
    mock_model.with_structured_output.assert_called_once_with(mock_topic_response)
    mock_model.with_structured_output.return_value.invoke.assert_called_once()

def test_extract_topics_empty_result(mock_config, mock_logger, mock_model, mock_topic_response):
    # Arrange
    transcript = "This is a sample transcript."
    language = "en"
    keyframes_descriptions = ["Keyframe 1 description", "Keyframe 2 description"]
    mock_model.with_structured_output.return_value.invoke.side_effect = Exception("Test exception")

    # Act
    topics = extract_topics(transcript, language, keyframes_descriptions)

    # Assert
    assert topics == []
    mock_logger.error.assert_called_with("Error while extracting topics... Test exception")
