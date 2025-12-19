import subprocess
import pathlib
import argparse
import psutil  #type:ignore
import socket
import ipaddress
from scapy.all import ARP, Ether, srp #type:ignore
from typing import Union, Tuple, Optional, List

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

def arp_check(target_ip, timeout=1)-> bool:
    nic_info = get_interface_lan(target_ip)
    if not nic_info:
        return False
    _,_,interface = nic_info
     # Construct an Ethernet frame + ARP request
    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    # Send the packet on the network
    answered, unanswered = srp(packet, timeout=timeout, iface=interface, verbose=False)
    
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
    if get_interface_lan(ip_address):
        if arp_check(ip_address):
            return True
    """
    if fast_icmp(ip_address) == 0:
        return True
    if slow_icmp(ip_address) == 0:
        return True
    """
    return False

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

