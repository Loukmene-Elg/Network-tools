import subprocess


def fast_icmp(ip:str)->int:
    try:
        # run the ping command only one time and it time out at 100 ms it return 0 if reached else 1
        test = subprocess.run(
            ["ping","-n", "1", "-w", "100", ip],
            capture_output=True,
            text=True,
            timeout=1)
        return test.returncode
    except subprocess.TimeoutExpired:
        return 1


def slow_icmp(ip:str)->int:
    try:
        # run the ping command only three time and it time out at 300 ms each it return 0 if reached else 1
        test = subprocess.run(
            ["ping","-n", "3", "-w", "300", ip],
            capture_output=True,
            text=True,
            timeout=3)
        return test.returncode
    except subprocess.TimeoutExpired:
        return 1 
    
