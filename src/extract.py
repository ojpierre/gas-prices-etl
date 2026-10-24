import json
import logging
from typing import Any, Dict, List, Optional, Union
import requests

try:
    from .config import settings
    from .mock_data import get_mock_gas_data
except ImportError:
    from config import settings
    from mock_data import get_mock_gas_data

logger = logging.getLogger(__name__)


def extract_state_prices(
    state: str,
    api_key: Optional[str] = None,
    timeout: int = 15,
    use_mock: bool = False,
) -> Dict[str, Any]:
    resolved_key = api_key or settings.api_key
    state_code = state.strip().upper()

    if use_mock or not resolved_key:
        if not resolved_key:
            logger.warning(
                "No CollectAPI key found in environment; falling back to mock gas price dataset for %s.",
                state_code,
            )
        return get_mock_gas_data(state_code)

    url = f"{settings.base_url}/gasPrice/stateUsaPrice"
    params = {"state": state_code}
    headers = {
        "content-type": "application/json",
        "authorization": f"apikey {resolved_key}",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if not data.get("success", False):
            error_msg = data.get("message", "CollectAPI returned an unsuccessful response")
            raise RuntimeError(f"API Error ({state_code}): {error_msg}")

        return data
    except requests.RequestException as exc:
        logger.error("Failed to fetch gas prices for state %s: %s", state_code, exc)
        raise


def extract(
    states: Union[str, List[str]] = "WA",
    api_key: Optional[str] = None,
    use_mock: bool = False,
) -> List[Dict[str, Any]]:
    if isinstance(states, str):
        state_list = [s.strip().upper() for s in states.split(",") if s.strip()]
    else:
        state_list = [s.strip().upper() for s in states if s.strip()]

    if not state_list:
        state_list = [settings.default_state]

    results: List[Dict[str, Any]] = []
    for state_code in state_list:
        logger.info("Extracting gas price data for state: %s", state_code)
        payload = extract_state_prices(
            state=state_code,
            api_key=api_key,
            use_mock=use_mock,
        )
        results.append(payload)

    return results