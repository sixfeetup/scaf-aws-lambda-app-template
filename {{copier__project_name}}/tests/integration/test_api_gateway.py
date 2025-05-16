import pytest
import requests
from unittest.mock import patch, MagicMock

@pytest.fixture
def api_gateway_url():
    return "https://mocked-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod/"

class TestApiGateway:
    @patch("requests.get")
    def test_api_gateway(self, mock_get, api_gateway_url):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "hello world"
        }
        mock_get.return_value = mock_response

        response = requests.get(api_gateway_url)
        
        assert response.status_code == 200
        assert response.json() == {"message": "hello world"}
        mock_get.assert_called_once_with(api_gateway_url)
