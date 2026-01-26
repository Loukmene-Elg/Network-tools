from netmon.core.interface import network_info
from netmon.utils.ip import create_subnet_hostes
from netmon.core.check import Single_host_check
from concurrent.futures import ThreadPoolExecutor, as_completed
def search():
    all_nics = network_info()

    output: dict[str, bool] = {}

    for address, subnet, interface in all_nics:
        if address is None or subnet is None:
            return {"there is a nic with no address or subnet": False}
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
                    print(f"Error checking {host_ip}: {e}")

    # Print nicely
    for ip, alive in output.items():
        if alive:
            print(f"{ip} is UP")

    return output