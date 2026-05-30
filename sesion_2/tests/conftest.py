# tests/conftest.py
# Configuración global de pytest para la Sesión 2

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: tests que requieren Ollama o Azure corriendo"
    )
    config.addinivalue_line(
        "markers", "unit: tests que no requieren servicios externos"
    )
