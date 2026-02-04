from typing import Dict

from netmon.utils.ip import sort_ip
from netmon.core.logger import logger


def print_output(search_result: Dict[str, bool], Alive: bool | None) -> None:
    sorted_result = sort_ip(search_result)
    alive_device: list[str] = []
    unalive_device: list[str] = []
    for host, status in sorted_result:
        if Alive is True and not status:
            continue
        if Alive is False and status:
            continue
        if status:
            logger.success(f"{host} is Alive \n")
            with open("netmon_scan_results.txt", "a") as f:
                f.write(f"{host} is Alive \n")
            alive_device.append(host)
        else:
            logger.info(f"{host} is Inactive \n")
            with open("netmon_scan_results.txt", "a") as f:
                f.write(f"{host} is Inactive \n")
            unalive_device.append(host)

    return
