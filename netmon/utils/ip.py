import ipaddress
from typing import List
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


def create_subnet_hostes(ip:str, mask:str, limit:int = 4096)->List[str|None]:
    try:
        network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
    except ValueError:
        return[]
    hosts: list[str|None] = []
    for host in network.hosts():
        if len(hosts) >= limit:
            return hosts
        current_ip = str(host)
        if current_ip != ip:
            hosts.append(current_ip)

    
    return hosts