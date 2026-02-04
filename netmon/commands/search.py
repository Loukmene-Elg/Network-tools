from netmon.core.interface import network_info
from netmon.utils.ip import create_subnet_hostes
from netmon.utils.output import print_output
from netmon.core.check import Single_host_check
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmon.core.logger import logger
from typing import Dict
def main(Alive:bool):
    all_nics = network_info()
    logger.info(f"  Detected {len(all_nics)} NICs")
    output: dict[str, bool] = {}

    for address, subnet, interface in all_nics:
        if address is None or subnet is None:
            logger.warning("No nic detected")
            return {"there is a nic with no address or subnet": False}
        logger.info(f"Scanning subnet {subnet} on interface {interface} with address {address}")
        hosts = create_subnet_hostes(ip=address,mask=subnet)
        nic_info: list[str | None] = [address, subnet, interface]
        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = {executor.submit(Single_host_check, str(host), nic_info): host for host in hosts}

            for future in as_completed(futures):
                host_ip = str(futures[future])
                try:
                    is_up = future.result()
                    output[host_ip] = is_up
                except Exception as e:
                    output[host_ip] = False
                    logger.warning(f"Error checking {host_ip}: {e}")

    # Print nicely
    print_output(search_result=output,Alive=Alive)
   
    return True

if __name__ == '__main__':
    import argparse
    