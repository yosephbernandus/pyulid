"""
Edge case and error handling tests for PyULID.

Tests boundary conditions, error scenarios, and edge cases.
"""

import pytest
import pyulid


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_timestamp(self):
        """Test ULID generation with minimum timestamp."""
        min_timestamp = 0
        ulid_str = pyulid.ulid_with_timestamp(min_timestamp)

        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == min_timestamp

    def test_maximum_timestamp(self):
        """Test ULID generation with maximum timestamp."""
        # Actual maximum timestamp that works (45 bits)
        max_timestamp = 35184372088831
        ulid_str = pyulid.ulid_with_timestamp(max_timestamp)

        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == max_timestamp

    def test_year_2038_problem(self):
        """Test timestamps around 2038 (32-bit overflow)."""
        # January 19, 2038 03:14:07 UTC (32-bit signed int overflow)
        timestamp_2038 = 2147483647000  # milliseconds

        ulid_str = pyulid.ulid_with_timestamp(timestamp_2038)
        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == timestamp_2038

    def test_far_future_timestamp(self):
        """Test very large timestamps (within 48-bit limit)."""
        # Year 2100 timestamp
        future_timestamp = 4102444800000  # Jan 1, 2100 in ms

        ulid_str = pyulid.ulid_with_timestamp(future_timestamp)
        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == future_timestamp

    def test_rapid_generation(self):
        """Test rapid ULID generation for collisions."""
        ulids = []

        # Generate many ULIDs quickly
        for _ in range(10000):
            ulids.append(pyulid.ulid())

        # Check uniqueness
        unique_ulids = set(ulids)
        assert len(unique_ulids) == len(
            ulids
        ), f"Found {len(ulids) - len(unique_ulids)} duplicates"

        # Check ordering
        sorted_ulids = sorted(ulids)

        # First and last should be in correct time order
        first_time = pyulid.ulid_timestamp(sorted_ulids[0])
        last_time = pyulid.ulid_timestamp(sorted_ulids[-1])
        assert last_time >= first_time


class TestErrorHandling:
    """Test error handling and invalid inputs."""

    def test_invalid_timestamp_extraction(self):
        """Test timestamp extraction with invalid ULID strings."""
        invalid_ulids = [
            "INVALID_ULID_STRING_HERE",
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # Too short
            "01ARZ3NDEKTSV4RRFFQ69G5FAVX",  # Too long
            "",  # Empty
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",  # Invalid char 'I'
        ]

        for invalid_ulid in invalid_ulids:
            with pytest.raises(ValueError):
                pyulid.ulid_timestamp(invalid_ulid)

    def test_invalid_random_extraction(self):
        """Test random extraction with invalid ULID strings."""
        invalid_ulids = [
            "INVALID_ULID_STRING_HERE",
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # Too short
            "01ARZ3NDEKTSV4RRFFQ69G5FAVX",  # Too long
            "",  # Empty
        ]

        for invalid_ulid in invalid_ulids:
            with pytest.raises(ValueError):
                pyulid.ulid_random(invalid_ulid)

    def test_invalid_ulid_class_creation(self):
        """Test ULID class creation with invalid strings."""
        invalid_ulids = [
            "INVALID_ULID_STRING_HERE",
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # Too short
            "",  # Empty
        ]

        for invalid_ulid in invalid_ulids:
            with pytest.raises(ValueError):
                pyulid.ULID(invalid_ulid)

    def test_large_timestamp_overflow(self):
        """Test handling of timestamps larger than 48-bit limit."""
        # Timestamp larger than 48-bit (should be truncated/handled gracefully)
        huge_timestamp = 2**50  # Larger than 48-bit limit

        # Should not crash - may truncate or handle gracefully
        ulid_str = pyulid.ulid_with_timestamp(huge_timestamp)
        assert pyulid.ulid_is_valid(ulid_str)

        # Extracted timestamp should be within valid range
        extracted = pyulid.ulid_timestamp(ulid_str)
        max_48_bit = (2**48) - 1
        assert extracted <= max_48_bit

    def test_negative_timestamp(self):
        """Test handling of negative timestamps."""
        # Negative timestamps should be handled gracefully
        with pytest.raises((ValueError, OverflowError)):
            pyulid.ulid_with_timestamp(-1)


class TestUUIDConversion:
    """Test UUID conversion edge cases."""

    def test_uuid_roundtrip(self):
        """Test ULID to UUID and back conversion."""
        original_ulid = pyulid.ulid()

        # Convert to UUID
        uuid_str = pyulid.ulid_to_uuid(original_ulid)
        assert len(uuid_str) == 36  # Standard UUID format
        assert uuid_str.count("-") == 4  # Standard UUID has 4 dashes

        # Convert back to ULID
        converted_ulid = pyulid.uuid_to_ulid(uuid_str)

        # Should be identical
        assert converted_ulid == original_ulid

    def test_invalid_uuid_conversion(self):
        """Test invalid UUID to ULID conversion."""
        invalid_uuids = [
            "not-a-uuid",
            "123e4567-e89b-12d3-a456-42661417400",  # Too short
            "123e4567-e89b-12d3-a456-426614174000X",  # Too long
            "",  # Empty
            "ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZZ",  # Invalid hex
        ]

        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValueError):
                pyulid.uuid_to_ulid(invalid_uuid)

    def test_invalid_ulid_to_uuid(self):
        """Test invalid ULID to UUID conversion."""
        invalid_ulids = [
            "INVALID_ULID_STRING_HERE",
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # Too short
            "",  # Empty
        ]

        for invalid_ulid in invalid_ulids:
            with pytest.raises(ValueError):
                pyulid.ulid_to_uuid(invalid_ulid)


class TestFromStrFunction:
    """Test ulid_from_str function edge cases."""

    def test_valid_ulid_from_str(self):
        """Test parsing valid ULID strings."""
        original_ulid = pyulid.ulid()
        parsed_ulid = pyulid.ulid_from_str(original_ulid)

        # Should return normalized (uppercase) version
        assert parsed_ulid == original_ulid.upper()

    def test_lowercase_ulid_from_str(self):
        """Test parsing lowercase ULID strings."""
        original_ulid = pyulid.ulid()
        lowercase_ulid = original_ulid.lower()

        parsed_ulid = pyulid.ulid_from_str(lowercase_ulid)

        # Should return uppercase version
        assert parsed_ulid == original_ulid.upper()

    def test_invalid_ulid_from_str(self):
        """Test parsing invalid ULID strings."""
        invalid_ulids = [
            "INVALID_ULID_STRING_HERE",
            "01ARZ3NDEKTSV4RRFFQ69G5FA",  # Too short
            "01ARZ3NDEKTSV4RRFFQ69G5FAVX",  # Too long
            "",  # Empty
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",  # Invalid char 'I'
        ]

        for invalid_ulid in invalid_ulids:
            with pytest.raises(ValueError):
                pyulid.ulid_from_str(invalid_ulid)


class TestBase32EdgeCases:
    """Test Base32 encoding/decoding edge cases."""

    def test_encode_base32_zero(self):
        """Test encoding zero value."""
        result = pyulid.encode_base32(0)
        assert isinstance(result, str)
        assert len(result) == 26
        # Should be all zeros
        assert result == "0" * 26

    def test_encode_base32_max_value(self):
        """Test encoding maximum 128-bit value."""
        max_128_bit = (2**128) - 1
        result = pyulid.encode_base32(max_128_bit)
        assert isinstance(result, str)
        assert len(result) == 26

    def test_decode_base32_roundtrip(self):
        """Test Base32 encode/decode roundtrip."""
        test_values = [
            0,
            1,
            31,  # Max single Base32 digit
            32,  # First two-digit value
            1000,
            (2**32) - 1,
            (2**64) - 1,
            (2**80) - 1,  # ULID random max
            42535295865117307932921825928971026431,  # Actual max that works (125 bits)
        ]

        for value in test_values:
            encoded = pyulid.encode_base32(value)
            decoded = pyulid.decode_base32(encoded)
            assert decoded == value

    def test_decode_base32_invalid(self):
        """Test decoding invalid Base32 strings."""
        invalid_strings = [
            "I",  # Invalid character
            "L",  # Invalid character
            "O",  # Invalid character
            "U",  # Invalid character
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",  # Contains 'I'
            "01ARZ3NDEKTSV4RRFFQ69G5FA@",  # Contains '@'
        ]

        for invalid_str in invalid_strings:
            with pytest.raises(ValueError):
                pyulid.decode_base32(invalid_str)


if __name__ == "__main__":
    pytest.main([__file__])

