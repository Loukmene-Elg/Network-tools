import subprocess
import pathlib
import argparse
from typing import Union

def check_host(ip_address:str)-> Union[dict[str,str], None]:
    subprocess.run(f"ping {ip_address}")

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
            if not len(parts) == 2 :
                print(f"Invalid format on line {line_number}")
                continue
            ip_address, hostname = parts
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
    print(load_data(path))

if __name__ == "__main__":
    main()

