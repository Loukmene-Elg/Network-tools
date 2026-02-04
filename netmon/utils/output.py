from typing import Dict
from netmon.utils.ip import sort_ip
from netmon.core.logger import logger
def print_output(search_result:Dict[str, bool], Alive: bool):
    sorted_result = sort_ip(search_result)
    alive_device = list()
    unalive_device = list()
    for host , status in sorted_result:
        if status:
            logger.success(f"{host} is Alive \n")#type: ignore
            with open("netmon_scan_results.txt", "a") as f:
                f.write(f"{host} is Alive \n")
            alive_device.append(host)
        else:
            logger.info(f"{host} is Inactive \n")
            with open("netmon_scan_results.txt", "a") as f:
                f.write(f"{host} is Inactive \n")
            unalive_device.append(host)
   
    return 