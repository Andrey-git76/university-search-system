"""Проверка доступности стенда для интеграционных QA-тестов."""

from __future__ import annotations

import os

import httpx

API_URL = os.getenv("QA_API_URL", os.getenv("E2E_API_URL", "http://localhost:8000"))
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:5173")


def is_api_available(timeout: float = 5.0) -> bool:
    try:
        response = httpx.get(f"{API_URL}/health", timeout=timeout)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def is_frontend_available(timeout: float = 5.0) -> bool:
    try:
        response = httpx.get(FRONTEND_URL, timeout=timeout)
        return response.status_code < 500
    except httpx.HTTPError:
        return False


def is_stack_available(require_frontend: bool = False) -> bool:
    if not is_api_available():
        return False
    if require_frontend and not is_frontend_available():
        return False
    return True
