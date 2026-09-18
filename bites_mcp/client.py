"""Thin HTTP client for a Bites deployment's public API (/api/v1/*)."""
import os
from typing import Any

import httpx


class BitesError(Exception):
    """Raised for anything that stops a Bites API call from succeeding:
    missing configuration, a network problem, or an error response."""


class BitesClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.environ.get("BITES_URL", "")).strip().rstrip("/")
        self.api_key = (api_key or os.environ.get("BITES_API_KEY", "")).strip()

        if not self.base_url:
            raise BitesError(
                "BITES_URL is not set. It should be the URL where your Bites app "
                "is deployed, e.g. https://your-app.vercel.app"
            )
        if not self.api_key:
            raise BitesError(
                "BITES_API_KEY is not set. It must match the API_KEY environment "
                "variable configured on your Bites deployment."
            )

        self._client = httpx.Client(
            base_url=f"{self.base_url}/api/v1",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            resp = self._client.request(method, path, **kwargs)
        except httpx.RequestError as e:
            raise BitesError(f"Could not reach Bites at {self.base_url}: {e}") from e

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code >= 400:
            message = data.get("error") if isinstance(data, dict) else None
            raise BitesError(message or f"Bites API returned HTTP {resp.status_code}")

        return data

    @staticmethod
    def _drop_none(fields: dict) -> dict[str, Any]:
        return {k: v for k, v in fields.items() if v is not None}

    def ping(self) -> dict:
        return self._request("GET", "/ping")

    def list_themes(self) -> list[dict]:
        return self._request("GET", "/themes")["themes"]

    def list_sites(self) -> list[dict]:
        return self._request("GET", "/sites")["sites"]

    def get_site(self, ident: str) -> dict:
        return self._request("GET", f"/sites/{ident}")["site"]

    def create_site(self, **fields) -> dict:
        return self._request("POST", "/sites", json=self._drop_none(fields))["site"]

    def update_site(self, ident: str, **fields) -> dict:
        return self._request("PATCH", f"/sites/{ident}", json=self._drop_none(fields))["site"]

    def delete_site(self, ident: str) -> dict:
        return self._request("DELETE", f"/sites/{ident}")
