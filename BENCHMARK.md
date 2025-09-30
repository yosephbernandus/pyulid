# ULID-Python Performance Benchmark

Performance comparison results of ulid-python with other Python ULID libraries.

## Benchmark Repository

Complete benchmark suite: [python_ulid_benchmark](https://github.com/yosephbernandus/dev-alchemy/tree/master/python_ulid_benchmark)

- Docker-based testing: [Docker README](https://github.com/yosephbernandus/dev-alchemy/blob/master/python_ulid_benchmark/docker-benchmark/README.md)
- Local machine testing: [Local README](https://github.com/yosephbernandus/dev-alchemy/blob/master/python_ulid_benchmark/README.md)

## Test Environments

### Docker Environment
- Python Version: 3.8
- Memory Limit: 512MB RAM
- CPU Limit: 2 cores
- Iterations: 100,000 per test

### Local Machine Environment  
- System: Ubuntu 20.04
- CPU: 8 cores
- Memory: 16GB
- Python Version: 3.12.3
- Iterations: 100,000 per test

## Performance Results

### Local Machine Results
| Library | Generation (ops/sec) | Parsing (ops/sec) | Overall Score |
|---------|---------------------|-------------------|---------------|
| ulid-python | 7,853,467 | 7,065,304 | 100.0% |
| py-ulid | 2,513,552 | 0 | 16.6% |
| ulid-py | 747,632 | 276,193 | 7.0% |
| python-ulid | 257,157 | 218,956 | 3.4% |

### Docker Results
| Library | Generation (ops/sec) | Parsing (ops/sec) | Overall Score |
|---------|---------------------|-------------------|---------------|
| ulid-python | 6,396,713 | 4,801,302 | 100% |
| py-ulid | 1,622,025 | 0 | 12.7% |
| ulid-py | 706,341 | 228,049 | 7.9% |
| python-ulid | 152,631 | 192,194 | 3.2% |

## Visual Results

### Local Machine
![Local Machine Results](https://github.com/yosephbernandus/dev-alchemy/blob/master/python_ulid_benchmark/quick_benchmark_results.png)

### Docker Environment
![Docker Results](https://github.com/yosephbernandus/dev-alchemy/blob/master/python_ulid_benchmark/docker-benchmark/ulid_benchmark_comparison.png)

## Libraries Tested

1. [ulid-python](https://pypi.org/project/ulid-python) - ULID library for Python
2. [python-ulid](https://pypi.org/project/python-ulid/) - Another ULID library for Python
3. [py-ulid](https://pypi.org/project/py-ulid/) - ULID implementation in Python
4. [ulid-py](https://pypi.org/project/ulid-py/) - ULID library for Python

## Test Categories

### Generation Test
Creating new ULID strings

### Parsing Test  
Timestamp extraction operations

---

For complete methodology and detailed results, see the [benchmark repository](https://github.com/yosephbernandus/dev-alchemy/tree/master/python_ulid_benchmark)
