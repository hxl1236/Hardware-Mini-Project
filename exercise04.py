"""
Use analog input with photocell
"""

import time
import machine
import json
import os

led = machine.Pin("LED", machine.Pin.OUT)
adc = machine.ADC(28)

def get_params(param_file: str) -> dict:
    """Reads parameters from a JSON file."""

    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")

    with open(param_file) as f:
        params = json.load(f)

    return params

def is_regular_file(path: str) -> bool:
    """Checks if a regular file exists."""

    S_IFREG = 0x8000

    try:
        return os.stat(path)[0] & S_IFREG != 0
    except OSError:
        return False
    
params = get_params("exercise04.json")

while True:
    value = adc.read_u16()
    print(value)
    duty_cycle = (value - params["min_bright"]) / (params["max_bright"] - params["min_bright"])
    led.high()
    time.sleep(params["blink_period"] * duty_cycle)
    led.low()
    time.sleep(params["blink_period"] * (1 - duty_cycle))
    

