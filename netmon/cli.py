import argparse
from netmon.commands import benchmark, monitor, scan, search

def main():
    parser = argparse.ArgumentParser(
        prog="netmon",
        description="Network monitoring & discovery tools"
    )
    sub = parser.add_subparsers(dest="command", required=True)


   

    # Benchmark command
    benchmark_parser = sub.add_parser("benchmark", help="Benchmark hosts (ARP vs ICMP)")
    benchmark_parser.add_argument("path", help="Path to the file with target IPs")
    benchmark_parser.add_argument("--runs", type=int, default=5, help="Number of runs per host")

    # You can add monitor, scan, search later
    # monitor_parser = sub.add_parser("monitor", help="Monitor hosts continuously")
    # scan_parser = sub.add_parser("scan", help="Scan network for devices")
    search_parser = sub.add_parser("search", help="Search a host")

    args = parser.parse_args()
    if args.command == "search":
        search.search()
    if args.command == "benchmark":
        benchmark.main(path=args.path, runs=args.runs)
