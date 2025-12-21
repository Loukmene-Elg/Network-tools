import argparse
from pathlib import Path
from netmon.core import arp, icmp, interface
from netmon.utils.data import load_data
from netmon.utils.ip import create_subnet_hostes
from netmon.core.arp import flush_arp
import time

def main(path: Path, runs: int):
    path = Path(path)
    data = load_data(path)

    nic = interface.network_info()
    for interfaces in nic:
        print("start here :")
        print(f"IP is: {interfaces[0]}, Subnet is: {interfaces[1]}, NIC is: {interfaces[2]}")
        print(create_subnet_hostes(interfaces[2],interfaces[0],interfaces[1]))
    
    if isinstance(data, str):
        print(data)
        return
    
    for ip in data:
        print(f"\n{'='*60}")
        print(f"Benchmarking {ip} ({data[ip]})")
        print(f"{'='*60}")
        
        nic_info = interface.get_interface_lan(ip)
        if not nic_info:
            print(f"  {ip} is not on the same LAN; skipping")
            continue
        
        # ============================================
        # TEST 1: Cold Cache (realistic first contact)
        # ============================================
        print("\n📊 COLD CACHE TEST (first contact scenario)")
        cold_arp_times = []
        cold_icmp_times = []
        
        for i in range(runs):
            # Cold ARP
            flush_arp(ip)
            time.sleep(0.1)  # Let the flush complete
            start = time.perf_counter()
            arp.windows_arp_check(ip, nic_info)
            cold_arp_times.append(time.perf_counter() - start)
            
            # Cold ICMP
            flush_arp(ip)
            time.sleep(0.1)
            start = time.perf_counter()
            icmp.fast_icmp(ip)
            cold_icmp_times.append(time.perf_counter() - start)
        
        avg_cold_arp = sum(cold_arp_times) / len(cold_arp_times)
        avg_cold_icmp = sum(cold_icmp_times) / len(cold_icmp_times)
        
        print(f"  Cold ARP:  {avg_cold_arp*1000:.2f}ms")
        print(f"  Cold ICMP: {avg_cold_icmp*1000:.2f}ms")
        print(f"  Winner: {'ARP' if avg_cold_arp < avg_cold_icmp else 'ICMP'}")
        
        # ============================================
        # TEST 2: Warm Cache (repeated checks)
        # ============================================
        print("\n🔥 WARM CACHE TEST (monitoring scenario)")
        warm_arp_times = []
        warm_icmp_times = []
        
        # Pre-populate cache
        arp.windows_arp_check(ip, nic_info)
        
        for i in range(runs):
            # Warm ARP (cache should be populated)
            start = time.perf_counter()
            arp.windows_arp_check(ip, nic_info)
            warm_arp_times.append(time.perf_counter() - start)
            
            # Warm ICMP
            start = time.perf_counter()
            icmp.fast_icmp(ip)
            warm_icmp_times.append(time.perf_counter() - start)
        
        avg_warm_arp = sum(warm_arp_times) / len(warm_arp_times)
        avg_warm_icmp = sum(warm_icmp_times) / len(warm_icmp_times)
        
        print(f"  Warm ARP:  {avg_warm_arp*1000:.2f}ms")
        print(f"  Warm ICMP: {avg_warm_icmp*1000:.2f}ms")
        print(f"  Winner: {'ARP' if avg_warm_arp < avg_warm_icmp else 'ICMP'}")
        
        # ============================================
        # SUMMARY
        # ============================================
        print(f"\n📈 SUMMARY FOR {ip}")
        print(f"  Cold: ARP is {(avg_cold_icmp/avg_cold_arp):.2f}x vs ICMP")
        print(f"  Warm: ARP is {(avg_warm_icmp/avg_warm_arp):.2f}x vs ICMP")
        print("\n"*3)
        
if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Benchmark hosts (ARP vs ICMP)")
    parser.add_argument("path", help="Path to the file with target IP")
    parser.add_argument("--runs", type=int, default=5, help="number of runs per host")
    args = parser.parse_args()

    main(args.path, args.runs)