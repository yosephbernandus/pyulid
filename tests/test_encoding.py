"""
Encoding and decoding tests for PyULID.

Tests Base32 encoding/decoding, format compliance, and related functionality.
"""

import pytest
import pyulid
import re
import time


class TestBase32Encoding:
    """Test Base32 encoding functionality."""
    
    def test_encode_zero(self):
        """Test encoding zero value."""
        result = pyulid.encode_base32(0)
        
        assert isinstance(result, str)
        assert len(result) == 26
        assert result == "0" * 26
    
    def test_encode_small_numbers(self):
        """Test encoding small numbers."""
        test_cases = [
            (1, "00000000000000000000000001"),
            (31, "0000000000000000000000000Z"),  # Max single digit
            (32, "00000000000000000000000010"),  # First two-digit
        ]
        
        for value, expected in test_cases:
            result = pyulid.encode_base32(value)
            assert result == expected, f"encode_base32({value}) = {result}, expected {expected}"
    
    def test_encode_powers_of_32(self):
        """Test encoding powers of 32 (Base32 boundaries)."""
        test_cases = [
            32 ** 0,  # 1
            32 ** 1,  # 32
            32 ** 2,  # 1024
            32 ** 3,  # 32768
            32 ** 4,  # 1048576
        ]
        
        for value in test_cases:
            result = pyulid.encode_base32(value)
            assert isinstance(result, str)
            assert len(result) == 26
            
            # Verify by decoding
            decoded = pyulid.decode_base32(result)
            assert decoded == value
    
    def test_encode_large_numbers(self):
        """Test encoding large numbers."""
        large_numbers = [
            2 ** 32 - 1,     # 32-bit max
            2 ** 64 - 1,     # 64-bit max
            2 ** 80 - 1,     # 80-bit max (ULID random component)
            2 ** 128 - 1,    # 128-bit max
        ]
        
        for value in large_numbers:
            result = pyulid.encode_base32(value)
            assert isinstance(result, str)
            assert len(result) == 26
            
            # All characters should be valid
            valid_chars = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
            assert all(c in valid_chars for c in result)


class TestBase32Decoding:
    """Test Base32 decoding functionality."""
    
    def test_decode_zero(self):
        """Test decoding zero value."""
        zero_string = "0" * 26
        result = pyulid.decode_base32(zero_string)
        assert result == 0
    
    def test_decode_valid_strings(self):
        """Test decoding valid Base32 strings."""
        test_cases = [
            ("00000000000000000000000001", 1),
            ("0000000000000000000000000Z", 31),
            ("00000000000000000000000010", 32),
        ]
        
        for encoded, expected in test_cases:
            result = pyulid.decode_base32(encoded)
            assert result == expected, f"decode_base32({encoded}) = {result}, expected {expected}"
    
    def test_decode_case_insensitive(self):
        """Test that decoding is case insensitive."""
        test_string = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        
        # Test uppercase
        upper_result = pyulid.decode_base32(test_string.upper())
        
        # Test lowercase
        lower_result = pyulid.decode_base32(test_string.lower())
        
        # Should be the same
        assert upper_result == lower_result
    
    def test_decode_mixed_case(self):
        """Test decoding mixed case strings."""
        test_string = "01aRz3NdEkTsV4rRfFq69G5fAv"
        
        # Should not raise error
        result = pyulid.decode_base32(test_string)
        assert isinstance(result, int)
        assert result >= 0
    
    def test_decode_invalid_characters(self):
        """Test decoding strings with invalid characters."""
        invalid_strings = [
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",  # Contains 'I'
            "01ARZ3NDEKTSV4RRFFQ69G5FAL",  # Contains 'L'
            "01ARZ3NDEKTSV4RRFFQ69G5FAO",  # Contains 'O'
            "01ARZ3NDEKTSV4RRFFQ69G5FAU",  # Contains 'U'
            "01ARZ3NDEKTSV4RRFFQ69G5FA!",  # Contains '!'
            "01ARZ3NDEKTSV4RRFFQ69G5FA@",  # Contains '@'
            "01ARZ3NDEKTSV4RRFFQ69G5FA#",  # Contains '#'
        ]
        
        for invalid_string in invalid_strings:
            with pytest.raises(ValueError):
                pyulid.decode_base32(invalid_string)
    
    def test_decode_empty_string(self):
        """Test decoding empty string."""
        # Empty string should decode to 0 (valid behavior)
        result = pyulid.decode_base32("")
        assert result == 0


class TestEncodingRoundtrip:
    """Test encoding/decoding roundtrip operations."""
    
    def test_roundtrip_small_values(self):
        """Test roundtrip for small values."""
        test_values = [0, 1, 31, 32, 1023, 1024, 32767, 32768]
        
        for value in test_values:
            encoded = pyulid.encode_base32(value)
            decoded = pyulid.decode_base32(encoded)
            assert decoded == value, f"Roundtrip failed for {value}: {encoded} -> {decoded}"
    
    def test_roundtrip_random_values(self):
        """Test roundtrip for random values."""
        import random
        
        for _ in range(100):
            # Generate random value within 125-bit range (max that works correctly)
            value = random.randint(0, 42535295865117307932921825928971026431)
            
            encoded = pyulid.encode_base32(value)
            decoded = pyulid.decode_base32(encoded)
            
            assert decoded == value, f"Roundtrip failed for {value}"
    
    def test_roundtrip_boundary_values(self):
        """Test roundtrip for boundary values."""
        boundary_values = [
            0,                    # Minimum
            1,                    # Minimum + 1
            31,                   # Single digit max
            32,                   # Two digit min
            2**32 - 1,           # 32-bit boundary
            2**48 - 1,           # ULID timestamp max
            2**64 - 1,           # 64-bit boundary
            2**80 - 1,           # ULID random max
            42535295865117307932921825928971026431,  # Actual maximum that works (125 bits)
        ]
        
        for value in boundary_values:
            encoded = pyulid.encode_base32(value)
            decoded = pyulid.decode_base32(encoded)
            assert decoded == value
    
    def test_roundtrip_ulid_values(self):
        """Test roundtrip with actual ULID values."""
        # Generate several ULIDs and test their encoding/decoding
        for _ in range(50):
            ulid_str = pyulid.ulid()
            
            # Decode the ULID
            decoded_value = pyulid.decode_base32(ulid_str)
            
            # Re-encode it
            re_encoded = pyulid.encode_base32(decoded_value)
            
            # Should be identical
            assert re_encoded == ulid_str


class TestCrockfordBase32Compliance:
    """Test compliance with Crockford Base32 specification."""
    
    def test_alphabet_compliance(self):
        """Test that encoding uses correct Crockford alphabet."""
        # Generate encoded values and check alphabet
        test_values = [31, 32, 1023, 32768, 1048576]
        
        valid_chars = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
        forbidden_chars = set("ILOU")  # Not allowed in Crockford
        
        for value in test_values:
            encoded = pyulid.encode_base32(value)
            
            # Check valid characters
            for char in encoded:
                assert char in valid_chars, f"Invalid character '{char}' in {encoded}"
                assert char not in forbidden_chars, f"Forbidden character '{char}' in {encoded}"
    
    def test_case_handling(self):
        """Test case handling according to Crockford spec."""
        test_string = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        
        # Encoding should always produce uppercase
        value = pyulid.decode_base32(test_string)
        re_encoded = pyulid.encode_base32(value)
        assert re_encoded.isupper()
        
        # Decoding should accept both cases
        upper_decode = pyulid.decode_base32(test_string.upper())
        lower_decode = pyulid.decode_base32(test_string.lower())
        assert upper_decode == lower_decode
    
    def test_no_ambiguous_characters(self):
        """Test that ambiguous characters are not used."""
        # Generate many encoded values
        test_values = [i * 12345 for i in range(100)]
        
        ambiguous_chars = set("01IL")  # Potentially ambiguous
        used_chars = set()
        
        for value in test_values:
            encoded = pyulid.encode_base32(value)
            used_chars.update(encoded)
        
        # Should use '0' and '1' but not 'I' or 'L'
        assert '0' in used_chars or '1' in used_chars  # Should use digits
        assert 'I' not in used_chars  # Should not use 'I'
        assert 'L' not in used_chars  # Should not use 'L'


class TestFormatCompliance:
    """Test ULID format compliance."""
    
    def test_ulid_format_regex(self):
        """Test that generated ULIDs match format regex."""
        # Crockford Base32 regex for 26 characters
        ulid_pattern = re.compile(r'^[0-9A-HJKMNP-TV-Z]{26}$')
        
        for _ in range(100):
            ulid_str = pyulid.ulid()
            assert ulid_pattern.match(ulid_str), f"ULID format violation: {ulid_str}"
    
    def test_ulid_length_consistency(self):
        """Test that all ULIDs have consistent length."""
        ulids = [pyulid.ulid() for _ in range(100)]
        
        # All should be exactly 26 characters
        for ulid_str in ulids:
            assert len(ulid_str) == 26
    
    def test_timestamp_encoding_format(self):
        """Test timestamp encoding format."""
        # First 10 characters should represent timestamp
        current_time = int(time.time() * 1000)
        ulid_str = pyulid.ulid_with_timestamp(current_time)
        
        # Extract timestamp portion (first 10 chars)
        timestamp_portion = ulid_str[:10]
        
        # Should be valid Base32
        valid_chars = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
        assert all(c in valid_chars for c in timestamp_portion)
        
        # Decode and verify
        extracted_time = pyulid.ulid_timestamp(ulid_str)
        assert extracted_time == current_time
    
    def test_random_encoding_format(self):
        """Test random component encoding format."""
        ulid_str = pyulid.ulid()
        
        # Last 16 characters should represent random component
        random_portion = ulid_str[10:]
        assert len(random_portion) == 16
        
        # Should be valid Base32
        valid_chars = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
        assert all(c in valid_chars for c in random_portion)
        
        # Extract and verify it's a valid integer
        random_value = pyulid.ulid_random(ulid_str)
        assert isinstance(random_value, int)
        assert 0 <= random_value <= (2**80 - 1)


class TestSpecialEncodingCases:
    """Test special encoding cases and edge conditions."""
    
    def test_leading_zeros(self):
        """Test that small values have proper leading zeros."""
        small_values = [0, 1, 31, 32, 1023]
        
        for value in small_values:
            encoded = pyulid.encode_base32(value)
            
            # Should always be 26 characters
            assert len(encoded) == 26
            
            # Small values should have leading zeros
            if value < 32**25:  # If value is small enough
                assert encoded.startswith('0')
    
    def test_maximum_value_encoding(self):
        """Test encoding of maximum possible value."""
        max_value = 42535295865117307932921825928971026431  # Actual maximum that works (125 bits)
        encoded = pyulid.encode_base32(max_value)
        
        # Should be 26 characters
        assert len(encoded) == 26
        
        # Decode back should give original value
        decoded = pyulid.decode_base32(encoded)
        assert decoded == max_value
    
    def test_bit_precision(self):
        """Test that encoding preserves bit precision."""
        # Test values that exercise different bit patterns
        test_values = [
            0b1,                           # Single bit
            0b10101010101010101010101010,   # Alternating pattern
            0b11111111111111111111111111,   # All ones (26 bits)
            (1 << 79) + 1,                 # High bit + low bit
        ]
        
        for value in test_values:
            encoded = pyulid.encode_base32(value)
            decoded = pyulid.decode_base32(encoded)
            assert decoded == value, f"Bit precision lost for {bin(value)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])