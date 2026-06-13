from __future__ import annotations

import base64
import json
import random
import time
from dataclasses import dataclass, field
from typing import Any, Mapping
from urllib.parse import urljoin

import httpx

try:
    from curl_cffi import requests as curl_requests
except Exception:  # pragma: no cover
    curl_requests = None

Json = dict[str, Any]

DEFAULT_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
DEFAULT_WEB_KEY = "a2c903cc-b31e-4547-9299-b6d07b7631ab"
API_KEY_TIME_SHIFT = 1111111111111


class APIError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


def now_ms() -> int:
    return int(time.time() * 1000)


def drop_empty(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None and value != ""}


def generate_oklink_api_key(now: int | None = None, *, web_key: str = DEFAULT_WEB_KEY) -> str:
    chars = list(web_key)
    rotated = "".join(chars[8:] + chars[:8])
    encrypted_time = f"{(now_ms() if now is None else now) + API_KEY_TIME_SHIFT}{random.randint(0, 999):03d}"
    return base64.b64encode(f"{rotated}|{encrypted_time}".encode()).decode()


@dataclass(slots=True)
class BaseClient:
    base_url: str
    timeout: float = 15.0
    headers: dict[str, str] = field(default_factory=dict)
    use_curl_cffi: bool = False

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self._client = httpx.Client(timeout=self.timeout, headers={"User-Agent": DEFAULT_UA, **self.headers})

    def close(self) -> None:
        self._client.close()

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        data: Any = None,
        headers: Mapping[str, str] | None = None,
        curl_cffi: bool | None = None,
    ) -> Json:
        url = self._url(path)
        merged_headers = {**self.headers, **(headers or {})}
        use_curl = self.use_curl_cffi if curl_cffi is None else curl_cffi
        if use_curl:
            if curl_requests is None:
                raise APIError("curl_cffi is not installed")
            resp = curl_requests.request(
                method,
                url,
                params=params,
                json=json_body,
                data=data,
                headers=merged_headers,
                timeout=self.timeout,
                impersonate="chrome124",
            )
            text = resp.text
            status = resp.status_code
        else:
            resp = self._client.request(method, url, params=params, json=json_body, data=data, headers=merged_headers)
            text = resp.text
            status = resp.status_code
        if status < 200 or status >= 300:
            raise APIError(f"{method} {url} failed with HTTP {status}", status_code=status, payload=text[:1000])
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise APIError(f"{method} {url} returned non-json", status_code=status, payload=text[:1000]) from exc
