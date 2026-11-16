import pytest

from stormtrace.extract import api_client
from stormtrace.extract.api_client import ExtractionError, fetch_daily_weather


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(params)
        return self.responses.pop(0)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(api_client.time, "sleep", lambda seconds: None)


def test_success_sends_era5_and_kolkata():
    session = FakeSession([FakeResponse(200, {"daily": {"time": []}})])
    result = fetch_daily_weather(9.9, 76.2, "2020-01-01", "2020-01-31", session=session)
    assert result == {"daily": {"time": []}}
    params = session.calls[0]
    assert params["models"] == "era5"
    assert params["timezone"] == "Asia/Kolkata"
    assert "sunshine_duration" in params["daily"]


def test_rate_limit_then_success():
    session = FakeSession([FakeResponse(429), FakeResponse(200, {"ok": True})])
    result = fetch_daily_weather(9.9, 76.2, "2020-01-01", "2020-01-31", session=session)
    assert result == {"ok": True}
    assert len(session.calls) == 2


def test_bad_request_raises_with_reason():
    session = FakeSession([FakeResponse(400, {"reason": "bad date"})])
    with pytest.raises(ExtractionError, match="bad date"):
        fetch_daily_weather(9.9, 76.2, "2020-01-01", "2020-01-31", session=session)


def test_repeated_server_errors_give_up():
    session = FakeSession([FakeResponse(500)] * 5)
    with pytest.raises(ExtractionError, match="Gave up"):
        fetch_daily_weather(9.9, 76.2, "2020-01-01", "2020-01-31", session=session)