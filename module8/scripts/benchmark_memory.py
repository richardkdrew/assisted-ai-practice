#!/usr/bin/env python3
"""Performance benchmark script for memory backends.

Compares performance of different memory storage backends:
1. File-based (JSON)
2. ChromaDB (vector database via MCP)
3. Graphiti (knowledge graph via MCP)

Metrics measured:
- Store operation latency
- Retrieve operation latency
- Retrieve by ID latency
- Memory usage
- Scalability (operations/second)

Usage:
    python scripts/benchmark_memory.py [--iterations 100] [--backends file,chroma]
"""

import argparse
import asyncio
import json
import os
import psutil
import time
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

from dotenv import load_dotenv

# Load environment
load_dotenv()

from investigator_agent.memory.file_store import FileMemoryStore
from investigator_agent.memory.protocol import Memory

# Import MCP components only if needed
try:
    from investigator_agent.mcp.client import MCPClient
    from investigator_agent.memory.mcp_store import MCPChromaMemoryStore, MCPGraphitiMemoryStore
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  MCP components not available. Only file-based backend will be benchmarked.")


class MemoryBackendBenchmark:
    """Benchmark harness for memory backends."""

    def __init__(self, backend_name: str, store: Any, is_async: bool = True):
        """Initialize benchmark.

        Args:
            backend_name: Name of the backend being tested
            store: Memory store instance
            is_async: Whether the store uses async methods
        """
        self.backend_name = backend_name
        self.store = store
        self.is_async = is_async
        self.results = {
            "backend": backend_name,
            "store_latencies": [],
            "retrieve_latencies": [],
            "retrieve_by_id_latencies": [],
            "memory_usage_mb": 0,
            "operations_per_second": 0,
        }

    async def warmup(self, count: int = 10):
        """Warm up the backend with some operations."""
        print(f"  Warming up {self.backend_name}...")
        for i in range(count):
            memory = self._create_test_memory(f"warmup_{i}")
            if self.is_async:
                await self.store.store(memory)
            else:
                self.store.store(memory)

    def _create_test_memory(self, memory_id: str) -> Memory:
        """Create a test memory object."""
        return Memory(
            id=memory_id,
            feature_id=f"FEAT-{memory_id.split('_')[-1]}",
            decision="ready" if int(memory_id.split('_')[-1]) % 2 == 0 else "not_ready",
            justification=f"Test justification for {memory_id}. This is a sample memory used for performance testing.",
            key_findings={
                "test_coverage": "95%",
                "performance_score": 8.5,
                "security_review": "passed",
                "stakeholder_approval": True,
            },
            timestamp=datetime.now(),
            metadata={"benchmark": True, "iteration": memory_id}
        )

    async def benchmark_store(self, iterations: int) -> None:
        """Benchmark store operations."""
        print(f"  Benchmarking store ({iterations} iterations)...")
        for i in range(iterations):
            memory = self._create_test_memory(f"bench_store_{i}")

            start = time.perf_counter()
            if self.is_async:
                await self.store.store(memory)
            else:
                self.store.store(memory)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

            self.results["store_latencies"].append(elapsed)

    async def benchmark_retrieve(self, iterations: int) -> None:
        """Benchmark retrieve operations."""
        print(f"  Benchmarking retrieve ({iterations} iterations)...")
        queries = [
            "production ready feature",
            "test coverage metrics",
            "security review results",
            "stakeholder approval status",
            "performance benchmarks",
        ]

        for i in range(iterations):
            query = queries[i % len(queries)]

            start = time.perf_counter()
            if self.is_async:
                memories = await self.store.retrieve(query=query, limit=5)
            else:
                memories = self.store.retrieve(query=query, limit=5)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

            self.results["retrieve_latencies"].append(elapsed)

    async def benchmark_retrieve_by_id(self, iterations: int) -> None:
        """Benchmark retrieve by ID operations."""
        print(f"  Benchmarking retrieve by ID ({iterations} iterations)...")
        for i in range(iterations):
            memory_id = f"bench_store_{i % min(iterations, 50)}"

            start = time.perf_counter()
            if self.is_async:
                memory = await self.store.retrieve_by_id(memory_id)
            else:
                memory = self.store.retrieve_by_id(memory_id)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

            self.results["retrieve_by_id_latencies"].append(elapsed)

    def measure_memory_usage(self) -> None:
        """Measure current memory usage."""
        process = psutil.Process()
        self.results["memory_usage_mb"] = process.memory_info().rss / (1024 * 1024)

    def calculate_throughput(self, total_operations: int, total_time_seconds: float) -> None:
        """Calculate operations per second."""
        self.results["operations_per_second"] = total_operations / total_time_seconds

    def print_results(self) -> None:
        """Print benchmark results."""
        print(f"\n{'=' * 80}")
        print(f"Results for {self.backend_name}")
        print(f"{'=' * 80}")

        def print_stats(operation: str, latencies: list[float]):
            if not latencies:
                print(f"{operation}: No data")
                return

            print(f"\n{operation}:")
            print(f"  Mean:   {mean(latencies):.2f} ms")
            print(f"  Median: {median(latencies):.2f} ms")
            print(f"  Min:    {min(latencies):.2f} ms")
            print(f"  Max:    {max(latencies):.2f} ms")
            if len(latencies) > 1:
                print(f"  StdDev: {stdev(latencies):.2f} ms")

        print_stats("Store Operation", self.results["store_latencies"])
        print_stats("Retrieve Operation", self.results["retrieve_latencies"])
        print_stats("Retrieve by ID", self.results["retrieve_by_id_latencies"])

        print(f"\nMemory Usage: {self.results['memory_usage_mb']:.2f} MB")
        print(f"Throughput: {self.results['operations_per_second']:.2f} ops/sec")


async def benchmark_file_backend(iterations: int) -> dict:
    """Benchmark file-based memory store."""
    print(f"\n{'=' * 80}")
    print("Benchmarking File-Based Memory Store")
    print(f"{'=' * 80}")

    # Create temporary directory for benchmark
    bench_dir = Path("/tmp/memory_benchmark_file")
    bench_dir.mkdir(exist_ok=True)

    # Clean up any existing data
    if (bench_dir / "index.json").exists():
        (bench_dir / "index.json").unlink()
    for mem_file in bench_dir.glob("*.json"):
        if mem_file.name != "index.json":
            mem_file.unlink()

    store = FileMemoryStore(bench_dir)
    benchmark = MemoryBackendBenchmark("File-Based", store, is_async=False)

    start_time = time.time()

    await benchmark.warmup()
    await benchmark.benchmark_store(iterations)
    await benchmark.benchmark_retrieve(iterations)
    await benchmark.benchmark_retrieve_by_id(iterations)

    total_time = time.time() - start_time
    benchmark.measure_memory_usage()
    benchmark.calculate_throughput(iterations * 3, total_time)
    benchmark.print_results()

    return benchmark.results


async def benchmark_chroma_backend(iterations: int) -> dict | None:
    """Benchmark ChromaDB MCP memory store."""
    if not MCP_AVAILABLE:
        print("⚠️  Skipping ChromaDB benchmark (MCP not available)")
        return None

    print(f"\n{'=' * 80}")
    print("Benchmarking ChromaDB MCP Memory Store")
    print(f"{'=' * 80}")

    chroma_url = os.getenv("MCP_CHROMA_URL", "http://localhost:8001/sse")

    try:
        # Connect to ChromaDB MCP server
        print(f"  Connecting to ChromaDB MCP: {chroma_url}")
        client = MCPClient(server_url=chroma_url, transport="sse")
        await client.connect()
        print("  ✅ Connected")

        store = MCPChromaMemoryStore(client, collection_name="benchmark_memories")
        await store.initialize()

        # Clear existing data
        await store.clear_all()
        await store.initialize()

        benchmark = MemoryBackendBenchmark("ChromaDB", store)

        start_time = time.time()

        await benchmark.warmup()
        await benchmark.benchmark_store(iterations)
        await benchmark.benchmark_retrieve(iterations)
        await benchmark.benchmark_retrieve_by_id(iterations)

        total_time = time.time() - start_time
        benchmark.measure_memory_usage()
        benchmark.calculate_throughput(iterations * 3, total_time)
        benchmark.print_results()

        await client.disconnect()

        return benchmark.results

    except Exception as e:
        print(f"❌ ChromaDB benchmark failed: {e}")
        print(f"   Make sure ChromaDB MCP server is running: docker-compose up chroma-mcp")
        return None


async def benchmark_graphiti_backend(iterations: int) -> dict | None:
    """Benchmark Graphiti MCP memory store."""
    if not MCP_AVAILABLE:
        print("⚠️  Skipping Graphiti benchmark (MCP not available)")
        return None

    print(f"\n{'=' * 80}")
    print("Benchmarking Graphiti MCP Memory Store")
    print(f"{'=' * 80}")

    graphiti_url = os.getenv("MCP_GRAPHITI_URL", "http://localhost:8000/sse")

    try:
        # Connect to Graphiti MCP server
        print(f"  Connecting to Graphiti MCP: {graphiti_url}")
        client = MCPClient(server_url=graphiti_url, transport="sse")
        await client.connect()
        print("  ✅ Connected")

        store = MCPGraphitiMemoryStore(client)

        benchmark = MemoryBackendBenchmark("Graphiti", store)

        start_time = time.time()

        await benchmark.warmup()
        await benchmark.benchmark_store(iterations)
        await benchmark.benchmark_retrieve(iterations)
        await benchmark.benchmark_retrieve_by_id(iterations)

        total_time = time.time() - start_time
        benchmark.measure_memory_usage()
        benchmark.calculate_throughput(iterations * 3, total_time)
        benchmark.print_results()

        await client.disconnect()

        return benchmark.results

    except Exception as e:
        print(f"❌ Graphiti benchmark failed: {e}")
        print(f"   Make sure Graphiti MCP server is running: docker-compose --profile graphiti up")
        return None


def save_results(results: list[dict], output_file: Path) -> None:
    """Save benchmark results to JSON file."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n📊 Results saved to: {output_file}")


def print_comparison(results: list[dict]) -> None:
    """Print comparison table of all backends."""
    if len(results) < 2:
        return

    print(f"\n{'=' * 80}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 80}")

    print(f"\n{'Backend':<15} {'Store (ms)':<15} {'Retrieve (ms)':<15} {'By ID (ms)':<15} {'Throughput'}")
    print("-" * 80)

    for result in results:
        backend = result["backend"]
        store_mean = mean(result["store_latencies"]) if result["store_latencies"] else 0
        retrieve_mean = mean(result["retrieve_latencies"]) if result["retrieve_latencies"] else 0
        by_id_mean = mean(result["retrieve_by_id_latencies"]) if result["retrieve_by_id_latencies"] else 0
        ops = result["operations_per_second"]

        print(f"{backend:<15} {store_mean:>12.2f}   {retrieve_mean:>12.2f}   {by_id_mean:>12.2f}   {ops:>8.1f} ops/s")


async def main():
    """Run memory backend benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark memory backends")
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of iterations per operation (default: 50)"
    )
    parser.add_argument(
        "--backends",
        type=str,
        default="file,chroma,graphiti",
        help="Comma-separated list of backends to test (default: file,chroma,graphiti)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.json",
        help="Output file for results (default: benchmark_results.json)"
    )

    args = parser.parse_args()
    backends = args.backends.split(",")

    print("=" * 80)
    print("MEMORY BACKEND PERFORMANCE BENCHMARK")
    print("=" * 80)
    print(f"Iterations per operation: {args.iterations}")
    print(f"Backends to test: {', '.join(backends)}")
    print("=" * 80)

    results = []

    if "file" in backends:
        result = await benchmark_file_backend(args.iterations)
        if result:
            results.append(result)

    if "chroma" in backends:
        result = await benchmark_chroma_backend(args.iterations)
        if result:
            results.append(result)

    if "graphiti" in backends:
        result = await benchmark_graphiti_backend(args.iterations)
        if result:
            results.append(result)

    # Print comparison
    print_comparison(results)

    # Save results
    output_file = Path(args.output)
    save_results(results, output_file)

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())
