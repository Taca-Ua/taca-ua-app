"""
Base service class for HTTP communication with microservices
"""

import logging
from typing import Any, Dict, Optional

import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for microservice communication"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = getattr(settings, "MICROSERVICE_TIMEOUT", 30)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to microservice

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            ValidationError: If the microservice returns an error
        """
        url = f"{self.base_url}{endpoint}"

        if headers is None:
            headers = {}

        headers.setdefault("Content-Type", "application/json")

        try:
            logger.info(f"Making {method} request to {url}")

            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )

            # Handle different status codes
            if response.status_code == 204:
                return {}

            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"detail": response.text}

                logger.error(
                    f"Microservice error: {response.status_code} - {error_data}"
                )
                raise ValidationError(error_data)

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {url}")
            raise ValidationError({"detail": "Microservice request timed out"})

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling {url}")
            raise ValidationError({"detail": "Cannot connect to microservice"})

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling {url}: {str(e)}")
            raise ValidationError({"detail": f"Request error: {str(e)}"})

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request"""
        return self._make_request("POST", endpoint, data=data, params=params)

    def put(
        self,
        endpoint: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, data=data, params=params)

    def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint, params=params)
