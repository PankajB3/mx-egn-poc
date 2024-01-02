import pytest
import os
from unittest.mock import patch, MagicMock
from assistant_gpt.assistant import start_assistant, assistant_works  


@pytest.fixture
def mock_assistant_works():
    with patch('assistant_gpt.assistant.assistant_works') as mock:
        yield mock

def test_start_assistant_success(mock_assistant_works):
    # Mock the client.beta.threads.create method
    with patch('assistant_gpt.assistant.start_assistant.client.beta.threads.create') as mock_create:
        # Set up mock return value for assistant_works
        mock_assistant_works.return_value = MagicMock()
        mock_assistant_works.return_value.data = [
            MagicMock(role='assistant', content=[MagicMock(text=MagicMock(value='Answer 1'))]),
            MagicMock(role='assistant', content=[MagicMock(text=MagicMock(value='Answer 2'))]),
        ]

        # Call the function
        result = start_assistant('eml_file', 'data_file', 'ex_file', 'fdb_file')

        # Assert the results
        assert result == ['Answer 2', 'Answer 1']
        mock_create.assert_called_once()
