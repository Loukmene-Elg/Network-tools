from typing import Union
from netmon.utils import is_valide_ip
import pathlib

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