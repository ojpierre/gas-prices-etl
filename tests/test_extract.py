import pytest
from src.extract import extract, extract_state_prices


def test_extract_mock_state():
    data = extract_state_prices("WA", use_mock=True)
    assert data["success"] is True
    assert data["result"]["state"] == "WA"
    assert len(data["result"]["cities"]) > 0


def test_extract_multiple_states():
    results = extract(states="WA,CA", use_mock=True)
    assert len(results) == 2
    state_codes = [r["result"]["state"] for r in results]
    assert "WA" in state_codes
    assert "CA" in state_codes


def test_extract_fallback_when_no_api_key(monkeypatch):
    monkeypatch.delenv("COLLECTAPI_KEY", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)

    data = extract_state_prices("TX", api_key="", use_mock=False)
    assert data["success"] is True
    assert data["result"]["state"] == "TX"


def test_extract_handles_api_failure(monkeypatch, mocker):
    mock_get = mocker.patch("requests.get")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"success": False, "message": "Rate limit exceeded"}
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="Rate limit exceeded"):
        extract_state_prices("WA", api_key="test_key", use_mock=False)
