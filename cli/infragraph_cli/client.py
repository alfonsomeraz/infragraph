"""HTTP client wrapping httpx for all InfraGraph API calls."""

from __future__ import annotations

from typing import Any

import httpx
import typer
from rich import print as rprint


class InfraGraphClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def __enter__(self) -> "InfraGraphClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self._client.close()

    def close(self) -> None:
        self._client.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _handle_error(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        rprint(f"[red]Error {response.status_code}: {detail}[/red]")
        raise typer.Exit(1)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.get(path, params=params)
        except httpx.ConnectError:
            rprint(f"[red]Connection refused — is the API running at {self.base_url}?[/red]")
            raise typer.Exit(1)
        self._handle_error(response)
        return response.json()

    def post(
        self,
        path: str,
        json: Any = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._client.post(path, json=json, files=files)
        except httpx.ConnectError:
            rprint(f"[red]Connection refused — is the API running at {self.base_url}?[/red]")
            raise typer.Exit(1)
        self._handle_error(response)
        return response.json()
