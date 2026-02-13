import pytest

from controller.file_utils import normalize_file_records

pytest.importorskip("pytest_benchmark")


def test_benchmark_normalize_file_records(benchmark):
    payload = [
        {"id": i, "name": f"file_{i}.txt", "size": i * 10}
        for i in range(1000)
    ]
    result = benchmark(normalize_file_records, payload)
    assert len(result) == 1000
