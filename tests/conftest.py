import json
from typing import Any, Dict
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@pytest.fixture
def sample_wa_raw_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "result": {
            "state": "WA",
            "cities": [
                {
                    "currency": "usd",
                    "name": "Seattle",
                    "gasoline": "4.899",
                    "midGrade": "5.099",
                    "premium": "5.329",
                    "diesel": "4.749",
                },
                {
                    "currency": "usd",
                    "name": "Spokane",
                    "gasoline": "4.459",
                    "midGrade": "4.699",
                    "premium": "4.949",
                    "diesel": "4.529",
                },
            ],
        },
    }


@pytest.fixture
def sample_raw_json_str(sample_wa_raw_payload: Dict[str, Any]) -> str:
    return json.dumps(sample_wa_raw_payload)


@pytest.fixture
def memory_db_engine() -> Engine:
    return create_engine("sqlite:///:memory:")
