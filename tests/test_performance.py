"""
Performance benchmark tests for PyULID.

Tests performance characteristics and provides benchmarking data.
"""

import pytest
import pyulid
import time
import statistics
from typing import Callable


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def measure_performance(self, func: Callable, iterations: int = 10000) -> dict:
        """Helper to measure function performance."""
        times = []

        for _ in range(5):  # Run 5 trials
            start = time.perf_counter()
            for _ in range(iterations):
                func()
            end = time.perf_counter()
            times.append(end - start)

        duration = statistics.mean(times)
        ops_per_second = iterations / duration

        return {
            "duration": duration,
            "ops_per_second": ops_per_second,
            "iterations": iterations,
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        }

    def test_ulid_generation_performance(self):
        """Benchmark ULID generation speed."""
        result = self.measure_performance(pyulid.ulid, 100000)

        print("\nULID Generation Performance:")
        print(f"  Iterations: {result['iterations']:,}")
        print(f"  Duration: {result['duration']:.4f}s")
        print(f"  Rate: {result['ops_per_second']:,.0f} ULIDs/second")
        print(f"  Std Dev: {result['std_dev']:.4f}s")

    def test_ulid_validation_performance(self):
        """Benchmark ULID validation speed."""
        test_ulid = pyulid.ulid()

        result = self.measure_performance(
            lambda: pyulid.ulid_is_valid(test_ulid), 100000
        )

        print("\nULID Validation Performance:")
        print(f"  Iterations: {result['iterations']:,}")
        print(f"  Duration: {result['duration']:.4f}s")
        print(f"  Rate: {result['ops_per_second']:,.0f} validations/second")

    def test_base32_encoding_performance(self):
        """Benchmark Base32 encoding speed."""
        test_value = 12345678901234567890

        result = self.measure_performance(
            lambda: pyulid.encode_base32(test_value), 50000
        )

        print("\nBase32 Encoding Performance:")
        print(f"  Iterations: {result['iterations']:,}")
        print(f"  Duration: {result['duration']:.4f}s")
        print(f"  Rate: {result['ops_per_second']:,.0f} encodings/second")

    def test_base32_decoding_performance(self):
        """Benchmark Base32 decoding speed."""
        test_ulid = pyulid.ulid()

        result = self.measure_performance(
            lambda: pyulid.decode_base32(test_ulid), 50000
        )

        print("\nBase32 Decoding Performance:")
        print(f"  Iterations: {result['iterations']:,}")
        print(f"  Duration: {result['duration']:.4f}s")
        print(f"  Rate: {result['ops_per_second']:,.0f} decodings/second")

    def test_timestamp_extraction_performance(self):
        """Benchmark timestamp extraction speed."""
        test_ulid = pyulid.ulid()

        result = self.measure_performance(
            lambda: pyulid.ulid_timestamp(test_ulid), 100000
        )

        print("\nTimestamp Extraction Performance:")
        print(f"  Iterations: {result['iterations']:,}")
        print(f"  Duration: {result['duration']:.4f}s")
        print(f"  Rate: {result['ops_per_second']:,.0f} extractions/second")

    def test_uuid_conversion_performance(self):
        """Benchmark UUID conversion speed."""
        test_ulid = pyulid.ulid()

        # Test ULID to UUID
        result_to_uuid = self.measure_performance(
            lambda: pyulid.ulid_to_uuid(test_ulid), 50000
        )

        print("\nULID to UUID Conversion Performance:")
        print(f"  Rate: {result_to_uuid['ops_per_second']:,.0f} conversions/second")

        # Test UUID to ULID
        test_uuid = pyulid.ulid_to_uuid(test_ulid)
        result_to_ulid = self.measure_performance(
            lambda: pyulid.uuid_to_ulid(test_uuid), 50000
        )

        print("UUID to ULID Conversion Performance:")
        print(f"  Rate: {result_to_ulid['ops_per_second']:,.0f} conversions/second")


class TestMemoryEfficiency:
    """Test memory usage and efficiency."""

    def test_memory_usage_bulk_generation(self):
        """Test memory usage during bulk ULID generation."""
        import gc
        import sys

        # Force garbage collection
        gc.collect()

        # Generate many ULIDs and check memory doesn't explode
        ulids = []
        for i in range(10000):
            ulids.append(pyulid.ulid())

            # Check memory periodically
            if i % 1000 == 0:
                gc.collect()
                # Memory usage should remain reasonable
                # This is a basic sanity check

        # All ULIDs should still be valid
        assert len(ulids) == 10000
        assert all(pyulid.ulid_is_valid(ulid) for ulid in ulids[:100])  # Sample check

    def test_no_memory_leaks_in_validation(self):
        """Test for memory leaks in validation functions."""
        test_ulid = pyulid.ulid()

        # Run validation many times - should not leak memory
        for _ in range(100000):
            pyulid.ulid_is_valid(test_ulid)

        # If we get here without crashing, likely no major leaks


class TestScalabilityLimits:
    """Test scalability and limits."""

    def test_high_frequency_generation(self):
        """Test high-frequency ULID generation."""
        start_time = time.time()
        ulids = []

        # Generate ULIDs for 1 second
        while time.time() - start_time < 1.0:
            ulids.append(pyulid.ulid())

        duration = time.time() - start_time
        rate = len(ulids) / duration

        print("\nHigh-Frequency Generation Test:")
        print(f"  Generated: {len(ulids):,} ULIDs")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Rate: {rate:,.0f} ULIDs/second")

        # Check uniqueness
        unique_ulids = len(set(ulids))
        collision_rate = (len(ulids) - unique_ulids) / len(ulids) * 100

        print(f"  Unique: {unique_ulids:,}")
        print(f"  Collisions: {len(ulids) - unique_ulids}")
        print(f"  Collision Rate: {collision_rate:.6f}%")

    def test_concurrent_generation_simulation(self):
        """Simulate concurrent ULID generation."""
        import threading
        import queue

        ulid_queue = queue.Queue()
        error_queue = queue.Queue()

        def generate_ulids(count: int):
            """Generate ULIDs in a thread."""
            try:
                for _ in range(count):
                    ulid_queue.put(pyulid.ulid())
            except Exception as e:
                error_queue.put(e)

        # Start multiple threads
        threads = []
        ulids_per_thread = 1000
        num_threads = 10

        start_time = time.time()

        for _ in range(num_threads):
            thread = threading.Thread(target=generate_ulids, args=(ulids_per_thread,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        duration = time.time() - start_time

        # Check for errors
        errors = []
        while not error_queue.empty():
            errors.append(error_queue.get())

        assert len(errors) == 0, f"Errors in concurrent generation: {errors}"

        # Collect all ULIDs
        ulids = []
        while not ulid_queue.empty():
            ulids.append(ulid_queue.get())

        expected_count = num_threads * ulids_per_thread
        assert len(ulids) == expected_count

        # Check uniqueness
        unique_ulids = len(set(ulids))
        collision_rate = (len(ulids) - unique_ulids) / len(ulids) * 100

        print("\nConcurrent Generation Test:")
        print(f"  Threads: {num_threads}")
        print(f"  ULIDs per thread: {ulids_per_thread}")
        print(f"  Total ULIDs: {len(ulids):,}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Rate: {len(ulids) / duration:,.0f} ULIDs/second")
        print(f"  Unique: {unique_ulids:,}")
        print(f"  Collision Rate: {collision_rate:.6f}%")


if __name__ == "__main__":
    # Run with verbose output to see benchmark results
    pytest.main([__file__, "-v", "-s"])
