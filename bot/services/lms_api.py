"""LMS API client service."""

import httpx
from config import get_settings


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.lms_api_base_url
        self._api_key = self._settings.lms_api_key
        self._headers = {"Authorization": f"Bearer {self._api_key}"}

    async def get_items(self) -> list[dict] | None:
        """
        Fetch all items (labs and tasks) from the backend.

        Returns:
            List of items, or None if the backend is unavailable.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/items/",
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            # Backend not running
            return None
        except httpx.HTTPStatusError as e:
            # HTTP error (4xx, 5xx)
            return None
        except Exception:
            # Any other error
            return None

    async def get_pass_rates(self, lab: str) -> list[dict] | None:
        """
        Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of pass rate data, or None if unavailable.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/analytics/pass-rates",
                    params={"lab": lab},
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            return None
        except httpx.HTTPStatusError:
            return None
        except Exception:
            return None


# Global client instance
_api_client: LMSAPIClient | None = None


def get_api_client() -> LMSAPIClient:
    """Get the LMS API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = LMSAPIClient()
    return _api_client
