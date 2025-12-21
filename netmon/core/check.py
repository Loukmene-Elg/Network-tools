from .interface import get_interface_lan
from .icmp import fast_icmp, slow_icmp
from .arp import windows_arp_check



def check_host(ip_address:str)-> bool:
    nic = get_interface_lan(ip_address)
    if nic and windows_arp_check(ip_address, nic):
        return True
    
    if fast_icmp(ip_address) == 0:
        return True
    return slow_icmp(ip_address) == 0

def Single_host_check(ip_addres, nic_info):
    if windows_arp_check(ip_addres, nic_info):
        return True
    
    if fast_icmp(ip_addres) == 0:
        return True
    return slow_icmp(ip_addres) == 0