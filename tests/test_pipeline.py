from src.main import run_pipeline


def test_pipeline_end_to_end_mock():
    rows = run_pipeline(
        states="WA,CA",
        database_url="sqlite:///:memory:",
        mode="append",
        use_mock=True,
    )
    assert rows == 7
