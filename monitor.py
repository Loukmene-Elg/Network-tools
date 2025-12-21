import subprocess
import pathlib
import argparse
import psutil  #type:ignore
import socket
import ipaddress
import time
from scapy.all import ARP, Ether, srp #type:ignore
from typing import Union, Tuple, Optional, List, Literal
from collections import defaultdict
import ctypes
import struct
import random

# Optimiszed Arp for windows Thanks for AI could't do it alone 
def windows_arp_check(ip: str,nic_info:List[Optional[str]]|None, timeout_ms: int = 100) -> bool:
    """
    Fast ARP check on Windows using SendARP with the correct LAN NIC.
    Returns True if host responds, False otherwise.
    """
    try:
        # Use your updated get_interface_lan() to find NIC on the same LAN
        
        if not nic_info:
            return False  # Host not on same LAN

        local_ip, _, _ = nic_info  # Extract the NIC IP
        assert local_ip is not None, "NIC IP should not be None"
        # Convert IPs to 32-bit integers (network byte order)
        ip_dest = struct.unpack("!I", socket.inet_aton(ip))[0]
        ip_source = struct.unpack("!I", socket.inet_aton(local_ip))[0]

        # Prepare buffer for MAC address (6 bytes)
        mac_addr = (ctypes.c_ubyte * 6)()
        mac_addr_len = ctypes.c_ulong(6)

        # Call SendARP with source IP of the correct NIC
        iphlpapi = ctypes.windll.iphlpapi
        result = iphlpapi.SendARP(
            ip_dest,           # Destination IP
            ip_source,         # Source IP = NIC IP
            ctypes.byref(mac_addr),
            ctypes.byref(mac_addr_len)
        )

        return result == 0

    except Exception as e:
        print(f"Error in windows_arp_check: {e}")
        return False


def compare_arp_icmp_with_metrics(
    ip: str,
    runs: int = 20
) -> Tuple[Literal["ARP", "ICMP", "Tie", "Error"], float, float]:
    nic_info = get_interface_lan(ip)
    
    arp_times = []
    icmp_times = []

    for _ in range(runs):
        methods = ["ARP", "ICMP"]
        random.shuffle(methods)

        for method in methods:
            if method == "ARP":
                start = time.perf_counter()
                arp_ok = windows_arp_check(ip, nic_info)
                arp_times.append(time.perf_counter() - start)
            else:
                start = time.perf_counter()
                icmp_ok = (fast_icmp(ip) == 0)
                icmp_times.append(time.perf_counter() - start)

    if not arp_times or not icmp_times:
        return "Error", 0.0, 0.0

    avg_arp = sum(arp_times) / len(arp_times)
    avg_icmp = sum(icmp_times) / len(icmp_times)

    if abs(avg_arp - avg_icmp) < 0.001:
        faster = "Tie"
    elif avg_arp < avg_icmp:
        faster = "ARP"
    else:
        faster = "ICMP"

    return faster, avg_arp, avg_icmp

def compare_arp_icmp(ip: str) -> Literal["ARP", "ICMP", "Tie", "Error"]|None:
    """
    Measures the time for arp_check() and fast_icmp() on a single host
    and returns which method is faster.
    """
    try:
        # Measure ARP
        nic = get_interface_lan(ip)
        if not nic:
            return None
        start_arp = time.perf_counter()
        arp_result = arp_check(ip,nic)
        end_arp = time.perf_counter()
        arp_time = end_arp - start_arp

        # Measure ICMP
        start_icmp = time.perf_counter()
        icmp_result = fast_icmp(ip)
        end_icmp = time.perf_counter()
        icmp_time = end_icmp - start_icmp

        # Compare times
        if not arp_result and not icmp_result:
            return "Error"  # Host not reachable by either method

        if abs(arp_time - icmp_time) < 0.001:  # within 1 ms
            return "Tie"
        elif arp_time < icmp_time:
            return "ARP"
        else:
            return "ICMP"

    except Exception as e:
        print(f"Error comparing ARP and ICMP for {ip}: {e}")
        return "Error"

def benchmark_hosts(hosts: dict[str, str], runs: int = 5):
    """
    Benchmark fast_icmp and arp_check on a list of hosts.
    hosts: dict mapping IP -> hostname
    runs: number of times to repeat each test
    """
    results = defaultdict(lambda: {"icmp": [], "arp": []})

    for ip in hosts:
        print(f"\nBenchmarking {ip} ({hosts[ip]})")
        nic = get_interface_lan(ip)
        if not nic:
            return None
        # Run multiple times
        for i in range(runs):
            # Measure fast_icmp
            start = time.perf_counter()
            fast_icmp(ip)
            end = time.perf_counter()
            results[ip]["icmp"].append(end - start)

            # Measure arp_check
            start = time.perf_counter()
            arp_check(ip, nic)
            end = time.perf_counter()
            results[ip]["arp"].append(end - start)

        # Print averages
        avg_icmp = sum(results[ip]["icmp"]) / runs
        avg_arp = sum(results[ip]["arp"]) / runs
        print(f"Average fast_icmp: {avg_icmp:.4f}s, Average arp_check: {avg_arp:.4f}s")

    return results

def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    print(f"{func.__name__} took {end - start:.4f}s, result: {result}")
    return result
def get_interface_lan(traget_ip:str)->List[Optional[str]] | None:

    if not is_valide_ip(traget_ip):
        return None

    network = network_info()
    if not network:
        return None
    for local_ip, local_mask, interface in network:
        current_ip4 = ipaddress.IPv4Network(f"{local_ip}/{local_mask}",strict=False)
        if ipaddress.IPv4Address(traget_ip) in current_ip4:
            return [local_ip, local_mask, interface]
    return None

def arp_check(target_ip,nic_info:List[Optional[str]],timeout=0.1)-> bool:
    if not nic_info:
        return False
    _,_,interface = nic_info
     # Construct an Ethernet frame + ARP request
    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    # Send the packet on the network
    answered, unanswered = srp(packet, timeout=timeout, iface=interface,retry=0, verbose=False)
    
    return bool(answered)  # True if host replied


def network_info()->list[List[Optional[str]]]:
    output = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                output.append([addr.address, addr.netmask, interface])
    return output

def fast_icmp(ip:str)->int:
    try:
        # run the ping command only one time and it time out at 100 ms it return 0 if reached else 1
        test = subprocess.run(
            ["ping","-n", "1", "-w", "100", ip],
            capture_output=True,
            text=True,
            timeout=1)
        return test.returncode
    except subprocess.TimeoutExpired:
        return 1

def slow_icmp(ip:str)->int:
    try:
        # run the ping command only three time and it time out at 300 ms each it return 0 if reached else 1
        test = subprocess.run(
            ["ping","-n", "3", "-w", "300", ip],
            capture_output=True,
            text=True,
            timeout=3)
        return test.returncode
    except subprocess.TimeoutExpired:
        return 1     

def check_host(ip_address:str)-> bool:
    nic = get_interface_lan(ip_address)
    if nic and arp_check(ip_address, nic):
        return True
    
    if fast_icmp(ip_address) == 0:
        return True
    return slow_icmp(ip_address) == 0

def is_valide_ip(ip:str) -> bool:
    # Split the input into a list of str ex: ["192"."168"."1"."1"]
    ip_parts = ip.split(".")
    if not len(ip_parts) == 4 :
        # When is not correctly formated ex: "192.168.1.1.1" or "192.168.1,1" or "19216811"
        return False
    for parts in ip_parts:
        # check if each part of the ip is a corrent number ex: ["abc"."168"."ze"."1"]
        if not parts.isdigit():
            return False
        if int(parts) > 255:
            # obvouisely no part should be bigger then 255
            return False
    
    return True

def load_data(path: pathlib.Path) -> Union[dict[str, str], str]:
    if not path.exists():
        return "Not a valide path"
    if not path.is_file():
        return "Not a file"
    if not path.suffix.lower() == ".txt":
        return "Not a text file"
    # init the dict 
    output: dict[str, str] = {}
    seen_lines: dict[str, int] = {}
    with path.open("r") as file:
        for line_number,line in enumerate(file, start=1):
            # remove end of line \n ex: 
            current_line = line.strip()
            if not current_line:
                # When line is empty
                continue
             # split the line into two part ex: ["192.168.1.1", "Computer A"]
            parts = current_line.split(maxsplit=1)
            # When format is incorrect ex: "192.168.1.1ComputerA"
            if not len(parts) == 2 :
                print(f"Invalid format on line {line_number}")
                continue
            ip_address, hostname = parts
            # Check if it is a valide IP 
            if is_valide_ip(ip_address):
                if ip_address in output:
                    print(f"Duplicated IP {ip_address}: previously on line {seen_lines[ip_address]}, now one line {line_number}")
                output[ip_address] = hostname
                seen_lines[ip_address] = line_number
            else:
                print(f"invalid IP on line {line_number}")
                continue
    return output


def main():
    parse = argparse.ArgumentParser(
        description="Basic Command to networking monitor tool"
    )

    parse.add_argument("Path", help="Select the path for the targets")
    args = parse.parse_args()
    path = pathlib.Path(args.Path)
    data = load_data(path)
    if isinstance(data, str):
        return print(data)
    for ip in data:
        test_result = check_host(ip) 
        if test_result:
            print(f"Test for {ip} {data[ip]} is UP")
        else:
            print(f"Test for {ip} {data[ip]} is DOWN") 
if __name__ == "__main__":
    main()

