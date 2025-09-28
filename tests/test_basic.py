"""
Basic functionality tests for PyULID.

Tests ULID generation, validation, and basic operations.
"""

import pytest
import pyulid
from datetime import datetime
import time


class TestBasicGeneration:
    """Test basic ULID generation functionality."""

    def test_ulid_generation(self):
        """Test basic ULID generation."""
        ulid_str = pyulid.ulid()

        # Check basic properties
        assert isinstance(ulid_str, str)
        assert len(ulid_str) == 26
        assert ulid_str.isupper()

        # Check character set (Crockford Base32)
        valid_chars = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
        assert all(c in valid_chars for c in ulid_str)

    def test_ulid_uniqueness(self):
        """Test that generated ULIDs are unique."""
        ulids = set()
        for _ in range(1000):
            ulid_str = pyulid.ulid()
            assert ulid_str not in ulids, f"Duplicate ULID generated: {ulid_str}"
            ulids.add(ulid_str)

    def test_ulid_generation_multiple(self):
        """Test generating multiple ULIDs in quick succession."""
        ulids = [pyulid.ulid() for _ in range(100)]

        # All should be unique
        assert len(set(ulids)) == 100

        # All should be valid format
        for ulid_str in ulids:
            assert len(ulid_str) == 26
            assert pyulid.ulid_is_valid(ulid_str)


class TestValidation:
    """Test ULID validation functionality."""

    def test_valid_ulid_validation(self):
        """Test validation of valid ULIDs."""
        # Test with generated ULID
        ulid_str = pyulid.ulid()
        assert pyulid.ulid_is_valid(ulid_str) is True

        # Test with known valid ULIDs
        valid_ulids = [
            "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "01BX5ZZKBKACTAV9WEVGEMMVRZ",
            "7ZZZZZZZZZZZZZZZZZZZZZZZZZ",
        ]

        for ulid_str in valid_ulids:
            assert pyulid.ulid_is_valid(ulid_str) is True

    def test_invalid_ulid_validation(self):
        """Test validation of invalid ULIDs."""
        invalid_ulids = [
            # Wrong length
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # 25 chars
            "01ARZ3NDEKTSV4RRFFQ69G5FAVX",  # 27 chars
            "",  # Empty
            # Invalid characters (I, L, O, U not allowed in Crockford Base32)
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",
            "01ARZ3NDEKTSV4RRFFQ69G5FAL",
            "01ARZ3NDEKTSV4RRFFQ69G5FAO",
            "01ARZ3NDEKTSV4RRFFQ69G5FAU",
            # Invalid characters (special chars)
            "01ARZ3NDEKTSV4RRFFQ69G5FA!",  # special char
            "01ARZ3NDEKTSV4RRFFQ69G5FA@",  # special char
            # Non-string types would cause errors, but we test string validation
            "IIIIIIIIIIIIIIIIIIIIIIIIII",  # Invalid chars (I not allowed)
        ]

        for invalid_ulid in invalid_ulids:
            assert pyulid.ulid_is_valid(invalid_ulid) is False

    def test_case_insensitive_validation(self):
        """Test that validation handles case properly."""
        ulid_str = pyulid.ulid()

        # Original should be valid
        assert pyulid.ulid_is_valid(ulid_str) is True

        # Lowercase version should be valid
        lowercase_ulid = ulid_str.lower()
        assert pyulid.ulid_is_valid(lowercase_ulid) is True


class TestTimestampExtraction:
    """Test timestamp extraction from ULIDs."""

    def test_current_timestamp_extraction(self):
        """Test extracting timestamp from current ULID."""
        before_time = int(time.time() * 1000)
        ulid_str = pyulid.ulid()
        after_time = int(time.time() * 1000)

        extracted_timestamp = pyulid.ulid_timestamp(ulid_str)

        # Timestamp should be within reasonable range
        assert before_time <= extracted_timestamp <= after_time

    def test_specific_timestamp_extraction(self):
        """Test extracting timestamp from ULID with specific timestamp."""
        # Use a known timestamp (2023-01-01 00:00:00 UTC)
        test_timestamp = 1672531200000  # milliseconds

        ulid_str = pyulid.ulid_with_timestamp(test_timestamp)
        extracted_timestamp = pyulid.ulid_timestamp(ulid_str)

        assert extracted_timestamp == test_timestamp

    def test_timestamp_ordering(self):
        """Test that ULIDs can be ordered by timestamp."""
        ulid1 = pyulid.ulid_with_timestamp(1000000000000)  # Earlier timestamp
        ulid2 = pyulid.ulid_with_timestamp(2000000000000)  # Later timestamp

        timestamp1 = pyulid.ulid_timestamp(ulid1)
        timestamp2 = pyulid.ulid_timestamp(ulid2)

        assert timestamp2 > timestamp1


class TestRandomExtraction:
    """Test random component extraction from ULIDs."""

    def test_random_extraction(self):
        """Test extracting random component from ULID."""
        ulid_str = pyulid.ulid()
        random_component = pyulid.ulid_random(ulid_str)

        # Random component should be a valid integer
        assert isinstance(random_component, int)
        assert random_component >= 0

        # Should be within 80-bit range (2^80 - 1)
        max_random = (2**80) - 1
        assert random_component <= max_random

    def test_random_uniqueness(self):
        """Test that random components are generally unique."""
        random_components = set()

        for _ in range(100):
            ulid_str = pyulid.ulid()
            random_component = pyulid.ulid_random(ulid_str)
            random_components.add(random_component)

        # Should have high uniqueness
        assert len(random_components) >= 95


class TestULIDClass:
    """Test the ULID class wrapper."""

    def test_ulid_class_creation(self):
        """Test creating ULID objects."""
        # Create without parameters
        ulid_obj = pyulid.ULID()
        assert isinstance(ulid_obj, pyulid.ULID)
        assert len(str(ulid_obj)) == 26

        # Create from string
        ulid_str = pyulid.ulid()
        ulid_obj2 = pyulid.ULID(ulid_str)
        assert str(ulid_obj2) == ulid_str

    def test_ulid_class_properties(self):
        """Test ULID class properties."""
        ulid_obj = pyulid.ULID()

        # Test timestamp property
        timestamp = ulid_obj.timestamp
        assert isinstance(timestamp, int)
        assert timestamp > 0

        # Test datetime property
        dt = ulid_obj.datetime
        assert isinstance(dt, datetime)

        # Test random property
        random_val = ulid_obj.random
        assert isinstance(random_val, int)
        assert random_val >= 0

        # Test string representation
        ulid_str = str(ulid_obj)
        assert len(ulid_str) == 26
        assert pyulid.ulid_is_valid(ulid_str)

    def test_ulid_class_comparison(self):
        """Test ULID comparison operations."""
        ulid1 = pyulid.ULID.with_timestamp(1000000000000)
        ulid2 = pyulid.ULID.with_timestamp(2000000000000)

        # Test equality
        ulid1_copy = pyulid.ULID(str(ulid1))
        assert ulid1 == ulid1_copy
        assert ulid1 != ulid2

        # Test ordering (lexicographic)
        assert ulid1 < ulid2  # ulid1 has earlier timestamp

        # Test string comparison
        assert ulid1 == str(ulid1)
        assert ulid1 != str(ulid2)


if __name__ == "__main__":
    pytest.main([__file__])
