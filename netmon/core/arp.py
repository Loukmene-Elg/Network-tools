import ctypes
from ctypes import wintypes  # ← Add this import!
import socket
import subprocess
from typing import Optional, List

def flush_arp(ip: str):
    """Flush the ARP cache entry for a specific IP (Windows)."""
    try:
        subprocess.run(["arp", "-d", ip], capture_output=True, text=True)
    except Exception as e:
        print(f"Warning: Could not flush ARP for {ip}: {e}")

def windows_arp_check(ip: str, nic_info: List[Optional[str]] | None, timeout_ms: int = 100) -> bool:
    """
    Fast ARP check on Windows using SendARP with the correct LAN NIC.
    Returns True if host responds, False otherwise.
    """
    try:
        flush_arp(ip)
        if not nic_info:
            print(f"  No NIC info for {ip}")
            return False

        local_ip, _, _ = nic_info
        if local_ip is None:
            print(f"  Local IP is None")
            return False
        
        # Convert string IPs to integers
        # Use 'little' byte order for Windows
        ip_dest = wintypes.DWORD(int.from_bytes(socket.inet_aton(ip), 'little'))
        ip_source = wintypes.DWORD(int.from_bytes(socket.inet_aton(local_ip), 'little'))

        # Prepare MAC address buffer
        mac_len = ctypes.c_ulong(6)
        mac_addr = (ctypes.c_ubyte * 6)()

        # Load the IP Helper API
        iphlpapi = ctypes.windll.iphlpapi
        
        # Call SendARP
        result = iphlpapi.SendARP(
            ip_dest,
            ip_source,
            ctypes.byref(mac_addr),
            ctypes.byref(mac_len)
        )

        if result == 0:
            # Success! Optionally print MAC
            mac_str = ':'.join(f'{b:02x}' for b in mac_addr)
            print(f"  ✓ ARP resolved: {ip} -> {mac_str}")
            return True
        else:
            # Decode common error codes
            error_messages = {
                67: "Network unreachable (ERROR_BAD_NET_NAME)",
                1168: "Element not found (ERROR_NOT_FOUND)",
                87: "Invalid parameter (ERROR_INVALID_PARAMETER)",
                1231: "Network location cannot be reached",
            }
            error_msg = error_messages.get(result, f"Unknown error {result}")
            print(f"  ✗ SendARP failed for {ip}: {error_msg}")
            return False

    except Exception as e:
        print(f"  Exception in windows_arp_check: {e}")
        import traceback
        traceback.print_exc()
        return False
