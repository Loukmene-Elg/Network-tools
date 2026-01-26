from typing import Optional, List
import socket
import ipaddress
import psutil #type:ignore
from netmon.utils.ip import is_valide_ip 

def network_info()->list[List[Optional[str]]]:
    output: list[List[Optional[str]]] = []
    interface_addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for interface, addrs in interface_addrs.items():
        if interface not in stats or not stats[interface].isup :
            continue
        for addr in addrs:
            if addr.family != socket.AF_INET :
                continue
            ip =addr.address
            try:
                ipv4_obj= ipaddress.IPv4Address(ip)
                if (ipv4_obj.is_loopback or ipv4_obj.is_link_local or ipv4_obj.is_unspecified):
                    continue
            except ValueError:
                continue

            output.append([addr.address, addr.netmask, interface])
    return output

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
