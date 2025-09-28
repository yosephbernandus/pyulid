"""
Pytest configuration and fixtures for PyULID tests.
"""

import pytest
import pyulid


@pytest.fixture
def sample_ulid():
    """Fixture providing a sample ULID for testing."""
    return pyulid.ulid()


@pytest.fixture
def sample_ulids():
    """Fixture providing multiple sample ULIDs for testing."""
    return [pyulid.ulid() for _ in range(10)]


@pytest.fixture
def known_ulid():
    """Fixture providing a known ULID for consistent testing."""
    return "01ARZ3NDEKTSV4RRFFQ69G5FAV"


@pytest.fixture
def ulid_with_known_timestamp():
    """Fixture providing a ULID with known timestamp."""
    timestamp = 1672531200000  # 2023-01-01 00:00:00 UTC
    ulid_str = pyulid.ulid_with_timestamp(timestamp)
    return ulid_str, timestamp


@pytest.fixture
def performance_context():
    """Fixture for performance testing context."""
    return {
        "min_generation_rate": 100000,  # ULIDs per second
        "min_validation_rate": 500000,  # Validations per second
        "min_decode_rate": 200000,  # Decodes per second
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "edge_case: mark test as an edge case test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add performance marker to performance tests
        if "performance" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)

        # Add slow marker to certain tests
        if any(
            keyword in item.nodeid.lower()
            for keyword in ["concurrent", "bulk", "memory"]
        ):
            item.add_marker(pytest.mark.slow)

        # Add edge_case marker to edge case tests
        if "edge" in item.nodeid.lower():
            item.add_marker(pytest.mark.edge_case)


@pytest.fixture(autouse=True)
def reset_state():
    """Fixture to ensure clean state between tests."""
    # Note: The Rust implementation uses global state
    # This fixture can be used to reset state if needed
    yield
    # Any cleanup code would go here

