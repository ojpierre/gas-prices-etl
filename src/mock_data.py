from typing import Any, Dict, List


SAMPLE_STATE_GAS_DATA: Dict[str, Dict[str, Any]] = {
    "WA": {
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
                {
                    "currency": "usd",
                    "name": "Tacoma",
                    "gasoline": "4.789",
                    "midGrade": "4.999",
                    "premium": "5.219",
                    "diesel": "4.699",
                },
                {
                    "currency": "usd",
                    "name": "Vancouver",
                    "gasoline": "4.659",
                    "midGrade": "4.899",
                    "premium": "5.119",
                    "diesel": "4.599",
                },
            ],
        },
    },
    "CA": {
        "success": True,
        "result": {
            "state": "CA",
            "cities": [
                {
                    "currency": "usd",
                    "name": "Los Angeles",
                    "gasoline": "5.199",
                    "midGrade": "5.419",
                    "premium": "5.629",
                    "diesel": "5.399",
                },
                {
                    "currency": "usd",
                    "name": "San Francisco",
                    "gasoline": "5.349",
                    "midGrade": "5.579",
                    "premium": "5.799",
                    "diesel": "5.499",
                },
                {
                    "currency": "usd",
                    "name": "San Diego",
                    "gasoline": "5.149",
                    "midGrade": "5.369",
                    "premium": "5.589",
                    "diesel": "5.329",
                },
            ],
        },
    },
    "TX": {
        "success": True,
        "result": {
            "state": "TX",
            "cities": [
                {
                    "currency": "usd",
                    "name": "Houston",
                    "gasoline": "3.129",
                    "midGrade": "3.399",
                    "premium": "3.699",
                    "diesel": "3.459",
                },
                {
                    "currency": "usd",
                    "name": "Dallas",
                    "gasoline": "3.199",
                    "midGrade": "3.459",
                    "premium": "3.759",
                    "diesel": "3.499",
                },
                {
                    "currency": "usd",
                    "name": "Austin",
                    "gasoline": "3.179",
                    "midGrade": "3.429",
                    "premium": "3.719",
                    "diesel": "3.489",
                },
            ],
        },
    },
}


def get_mock_gas_data(state: str) -> Dict[str, Any]:
    state_upper = state.upper()
    if state_upper in SAMPLE_STATE_GAS_DATA:
        return SAMPLE_STATE_GAS_DATA[state_upper]

    return {
        "success": True,
        "result": {
            "state": state_upper,
            "cities": [
                {
                    "currency": "usd",
                    "name": f"Metro {state_upper}",
                    "gasoline": "3.750",
                    "midGrade": "3.950",
                    "premium": "4.200",
                    "diesel": "3.900",
                }
            ],
        },
    }
