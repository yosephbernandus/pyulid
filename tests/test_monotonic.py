"""
Monotonic ULID generation and state management tests.

Tests monotonic ordering, state management, and related functionality.
"""

import pytest
import pyulid
import time
from typing import List


class TestMonotonicGeneration:
    """Test monotonic ULID generation."""

    def test_basic_monotonic_generation(self):
        """Test basic monotonic ULID generation."""
        ulid1 = pyulid.ulid()
        ulid2 = pyulid.ulid()

        # Both should be valid
        assert pyulid.ulid_is_valid(ulid1)
        assert pyulid.ulid_is_valid(ulid2)

        # Should be different
        assert ulid1 != ulid2

        # Should be lexicographically ordered
        assert ulid1 <= ulid2  # Second should be >= first

    def test_monotonic_ordering_same_millisecond(self):
        """Test monotonic ordering within same millisecond."""
        ulids = []

        # Generate many ULIDs
        for _ in range(100):
            ulids.append(pyulid.ulid())

        # All should be unique
        assert len(set(ulids)) == len(ulids)

        # Check that they are lexicographically ordered
        sorted_ulids = sorted(ulids)
        assert ulids == sorted_ulids, "ULIDs not generated in monotonic order"

        # Check timestamps - many should have same timestamp
        timestamps = [pyulid.ulid_timestamp(ulid) for ulid in ulids]
        unique_timestamps = set(timestamps)

        # Should have fewer unique timestamps than ULIDs
        assert len(unique_timestamps) < len(ulids)

        print(
            f"Generated {len(ulids)} ULIDs with {len(unique_timestamps)} unique timestamps"
        )

    def test_monotonic_across_time_boundaries(self):
        """Test monotonic ordering across time boundaries."""
        timestamp1 = 1000000000000
        timestamp2 = 2000000000000

        ulids_batch1 = [pyulid.ulid_with_timestamp(timestamp1) for _ in range(10)]
        ulids_batch2 = [pyulid.ulid_with_timestamp(timestamp2) for _ in range(10)]

        # All ULIDs should be unique
        all_ulids = ulids_batch1 + ulids_batch2
        assert len(set(all_ulids)) == len(all_ulids)

        # All ULIDs from batch2 should be > all ULIDs from batch1
        max_batch1 = max(ulids_batch1)
        min_batch2 = min(ulids_batch2)

        assert max_batch1 < min_batch2, "Ordering violated across time boundaries"

    def test_rapid_monotonic_generation(self):
        """Test rapid monotonic generation with fixed count."""
        # Generate a fixed number of ULIDs instead of time-based loop
        ulids = [pyulid.ulid() for _ in range(1000)]

        print(f"Generated {len(ulids)} ULIDs")

        # All should be unique
        assert len(set(ulids)) == len(ulids)

        # Should be monotonic
        assert ulids == sorted(ulids)

        # Check that timestamps are reasonable
        timestamps = [pyulid.ulid_timestamp(ulid) for ulid in ulids]
        assert all(isinstance(ts, int) and ts > 0 for ts in timestamps)


class TestStateManagement:
    """Test internal state management."""

    def test_state_persistence_across_calls(self):
        """Test that state persists across ULID generation calls."""
        # Generate first ULID
        ulid1 = pyulid.ulid()
        timestamp1 = pyulid.ulid_timestamp(ulid1)
        random1 = pyulid.ulid_random(ulid1)

        # Generate second ULID immediately
        ulid2 = pyulid.ulid()
        timestamp2 = pyulid.ulid_timestamp(ulid2)
        random2 = pyulid.ulid_random(ulid2)

        if timestamp1 == timestamp2:
            # Same timestamp - should increment random
            assert random2 == random1 + 1, f"Expected increment: {random1} -> {random2}"
        else:
            # Different timestamp - new random value
            assert timestamp2 > timestamp1

    def test_timestamp_change_resets_random(self):
        """Test that timestamp changes affect random component."""
        timestamp1 = 1000000000000
        timestamp2 = 2000000000000

        ulid1 = pyulid.ulid_with_timestamp(timestamp1)
        ulid2 = pyulid.ulid_with_timestamp(timestamp2)

        extracted_timestamp1 = pyulid.ulid_timestamp(ulid1)
        extracted_timestamp2 = pyulid.ulid_timestamp(ulid2)

        # Should have different timestamps
        assert extracted_timestamp2 > extracted_timestamp1

        # Random components should be valid integers
        random1 = pyulid.ulid_random(ulid1)
        random2 = pyulid.ulid_random(ulid2)

        assert isinstance(random1, int)
        assert isinstance(random2, int)

    def test_overflow_behavior(self):
        """Test behavior when random component might overflow."""
        # This is hard to test directly since we'd need 2^80 increments
        # But we can test the boundary conditions

        # Generate many ULIDs quickly to trigger increment behavior
        ulids = []
        for _ in range(10000):
            ulids.append(pyulid.ulid())

        # All should be valid and unique
        assert len(set(ulids)) == len(ulids)
        assert all(pyulid.ulid_is_valid(ulid) for ulid in ulids)

        # Should maintain monotonic ordering
        assert ulids == sorted(ulids)


class TestTimestampSpecificGeneration:
    """Test ULID generation with specific timestamps."""

    def test_ulid_with_timestamp(self):
        """Test generating ULID with specific timestamp."""
        # Test with current timestamp
        current_timestamp = int(time.time() * 1000)
        ulid_str = pyulid.ulid_with_timestamp(current_timestamp)

        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == current_timestamp

    def test_ulid_with_historical_timestamp(self):
        """Test generating ULID with historical timestamp."""
        # Unix epoch (1970-01-01)
        historical_timestamp = 0
        ulid_str = pyulid.ulid_with_timestamp(historical_timestamp)

        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == historical_timestamp

    def test_ulid_with_future_timestamp(self):
        """Test generating ULID with future timestamp."""
        # Year 2050
        future_timestamp = 2524608000000  # Jan 1, 2050 in ms
        ulid_str = pyulid.ulid_with_timestamp(future_timestamp)

        assert pyulid.ulid_is_valid(ulid_str)
        assert pyulid.ulid_timestamp(ulid_str) == future_timestamp

    def test_multiple_ulids_same_timestamp(self):
        """Test generating multiple ULIDs with same timestamp."""
        timestamp = int(time.time() * 1000)

        ulids = []
        for _ in range(100):
            ulids.append(pyulid.ulid_with_timestamp(timestamp))

        # All should have same timestamp
        for ulid_str in ulids:
            assert pyulid.ulid_timestamp(ulid_str) == timestamp

        # All should be unique (different random components)
        assert len(set(ulids)) == len(ulids)

        # Note: ulid_with_timestamp() generates random values, not monotonic
        # So they won't necessarily be in lexicographic order
        # This is correct behavior - monotonic ordering only applies to ulid() function


class TestClassBasedMonotonic:
    """Test monotonic behavior with ULID class."""

    def test_ulid_class_ordering(self):
        """Test ULID class comparison and ordering."""
        ulid1 = pyulid.ULID.with_timestamp(1000000000000)
        ulid2 = pyulid.ULID.with_timestamp(2000000000000)

        # Test comparison operators
        assert ulid1 != ulid2
        assert ulid1 < ulid2  # Should be ordered
        assert ulid2 > ulid1
        assert ulid1 <= ulid2
        assert ulid2 >= ulid1

    def test_ulid_class_with_timestamp_ordering(self):
        """Test ULID class with specific timestamps."""
        timestamp1 = 1000000000000  # Earlier timestamp
        timestamp2 = 2000000000000  # Later timestamp

        ulid1 = pyulid.ULID.with_timestamp(timestamp1)
        ulid2 = pyulid.ULID.with_timestamp(timestamp2)

        assert ulid1.timestamp == timestamp1
        assert ulid2.timestamp == timestamp2
        assert ulid1 < ulid2

    def test_ulid_class_sorting(self):
        """Test sorting ULID objects."""
        ulids = []

        # Create ULIDs with various timestamps
        for i in range(10):
            timestamp = 1000000000000 + (i * 1000)  # 1 second apart
            ulids.append(pyulid.ULID.with_timestamp(timestamp))

        # Shuffle and sort
        import random

        random.shuffle(ulids)
        sorted_ulids = sorted(ulids)

        # Should be in timestamp order
        timestamps = [ulid.timestamp for ulid in sorted_ulids]
        assert timestamps == sorted(timestamps)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
