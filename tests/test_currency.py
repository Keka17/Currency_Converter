import unittest
from unittest.mock import patch, mock_open, MagicMock
from app.tasks.exchange_rate_api import get_actual_rates
from app.main import app
from app.core.security import decode_jwt_token
from tests.conftest import client


class TestCeleryTask(unittest.TestCase):
    """
    Test the background task for fetching exchange rates
    and updating the local JSON storage.
    """

    @patch("app.tasks.exchange_rate_api.requests.get")  # API request
    async def test_get_actual_rates_save_json(self, mock_get: MagicMock):
        """
        Verify the full cycle of the background task:
        external API request -> JSON data parsing -> save to local file.
        """
        # Fake response from an external API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "updated": 1768593649,
            "base": "USD",
            "rates": {"USD": 1.0, "EUR": 0.86, "RUB": 77.9},
        }

        mock_get.return_value = mock_response

        # Simulate file operations without touching the filesystem
        m_open = mock_open()
        with patch("builtins.open", m_open):
            get_actual_rates()

        # Check if the request was sent to API
        mock_get.assert_called_once()

        # Check if the file was opened for writing and something was written
        m_open.assert_called_once_with("app/json/rates.json", "w", encoding="utf-8")


class TestConverterApi(unittest.TestCase):
    """
    Test for the currency converter API endpoint: POST /currency/converter.
    Another test return Error 400: Invalid code.
    """

    @patch(
        "app.api.endpoints.currency.get_actual_rates_data"
    )  # Replace JSON reading function
    async def test_convert_logic_success(self, mock_get_file_data: MagicMock):

        # Mock implementation for Dependency (JWT decoding)
        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        # Dependency override mechanism for the auth dependency
        # It replaces real 'decode_jwt_token' function with mock for this test
        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_file_data.return_value = {"USD": 1.0, "EUR": 0.86, "RUB": 77.9}

        payload = {"code_1": "EUR", "code_2": "RUB", "k": 100}
        headers = {"Authorization": "Bearer token"}

        # Request to the API endpoint
        response = await client.post(
            "/currency/converter", json=payload, headers=headers
        )

        # Clear overrides after running the test,
        # future requests run with the original dependencies
        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)  # same as ==
        result_data = response.json()

        # x = 0.86, y = 77.9 -> 100 EUR =  77.9 / 0.86 * 100 = 9,058.14
        self.assertIn("9,058.14", result_data["message"])

        # Check if the data reading function was called once
        mock_get_file_data.assert_called_once()

    @patch("app.api.endpoints.currency.get_actual_rates_data")
    async def test_convert_invalid_code(self, mock_get_file_data: MagicMock):

        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_file_data.return_value = {"USD": 1.0, "EUR": 0.86, "RUB": 77.9}

        payload = {"code_1": "EU", "code_2": "RUB", "k": 100}
        headers = {"Authorization": "Bearer token"}

        response = await client.post(
            "/currency/converter", json=payload, headers=headers
        )
        print(f"🍕 DEBUG {response.json()}")

        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 400)

        result_data = response.json()

        self.assertEqual(result_data["error_code"], "INVALID_CODE")


class TestCurrenciesList(unittest.TestCase):
    """
    Test for getting a list of available currencies: POST /currency/list.
    """

    @patch("app.api.endpoints.currency.get_codes_names")
    async def test_get_currencies_list(self, mock_get_codes: MagicMock):

        # Setup dependecy override (JWT auth)
        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_codes.return_value = {
            "USD": "🇺🇸 United States dollar",
            "EUR": "🇪🇺 Euro",
            "RUB": "🇷🇺 Russian ruble",
        }

        headers = {"Authorization": "Bearer token"}

        response = await client.get("/currency/list", headers=headers)

        # Clean up overrides
        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)

        result_data = response.json()
        self.assertEqual(result_data["message"], "Available currencies for conversion")

        self.assertIn("USD", result_data["currencies"])
        self.assertEqual(result_data["currencies"]["EUR"], "🇪🇺 Euro")

        mock_get_codes.assert_called_once()


class TestCurrenciesActualRates(unittest.TestCase):
    """
    Test for getting an actual rates of currencies: POST /currency/actual_rates.
    """

    @patch("app.api.endpoints.currency.get_actual_rates_data")
    async def test_get_currencies_list(self, mock_get_file_data: MagicMock):

        # Setup dependecy override (JWT auth)
        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_file_data.return_value = {"USD": 1.0, "EUR": 0.86, "RUB": 77.9}

        headers = {"Authorization": "Bearer token"}
        response = await client.get("/currency/actual_rates", headers=headers)

        # Clean up overrides
        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)

        result_data = response.json()
        self.assertEqual(
            result_data["message"],
            "Actual currencies rates. Base currency: 💵 USD (1 USD = value [Currency])",
        )

        self.assertIn("RUB", result_data["rates"])
        self.assertEqual(result_data["rates"]["EUR"], 0.86)

        mock_get_file_data.assert_called_once()


class TestSpecificCurrencyRate(unittest.TestCase):
    """
    Test for getting specific currency rates: GET /currency/actual_rate?code.
    Another test return Error 400: Invalid code.
    """

    @patch("app.api.endpoints.currency.get_actual_rates_data")
    async def test_get_specific_rate_success(self, mock_get_file_data: MagicMock):

        # Setup dependecy override (JWT auth)
        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_file_data.return_value = {"USD": 1.0, "EUR": 0.86, "RUB": 77.9}

        headers = {"Authorization": "Bearer token"}
        target_codes = ["EUR", "RUB"]

        response = await client.get(
            "/currency/actual_rate", params={"codes": target_codes}, headers=headers
        )

        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)

        result_data = response.json()

        self.assertIn(str(target_codes), result_data["message"])

        self.assertEqual(len(result_data["rate"]), 2)
        self.assertEqual(result_data["rate"]["EUR"], 0.86)
        self.assertEqual(result_data["rate"]["RUB"], 77.9)
        self.assertNotIn("JPY", result_data["rate"])

        mock_get_file_data.assert_called_once()

    @patch("app.api.endpoints.get_actual_rates_data")
    async def test_get_specific_rate_invalid_code(self, mock_get_file_data: MagicMock):

        # Setup dependecy override (JWT auth)
        def mock_decode_jwt_token():
            return {"token_type": "access", "sub": "testuser"}

        app.dependency_overrides[decode_jwt_token] = mock_decode_jwt_token

        mock_get_file_data.return_value = {"USD": 1.0, "EUR": 0.86, "RUB": 77.9}

        headers = {"Authorization": "Bearer token"}
        target_code = ["RU"]

        response = await client.get(
            "/currency/actual_rate", params={"codes": target_code}, headers=headers
        )

        app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 400)

        result_data = response.json()

        self.assertEqual(result_data["error_code"], "INVALID_CODE")
