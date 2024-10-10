#!/usr/bin/python3

import sys
from pathlib import Path
from atdf_parse import is_valid_device


def get_ifdef():
    yield "#if MCU_NAME == "
    while True:
        yield "#elif MCU_NAME == "


header_path = Path("generated_headers/mcu")
header_path.mkdir(parents=True, exist_ok=True)

source = open(header_path / "io.hpp", "w")
source.write("#pragma once\n\n")

atdf_dir = Path(sys.argv[1]) / "atdf"
device_list = [x for x in atdf_dir.glob("*.atdf") if is_valid_device(open(x))]

ifdef = get_ifdef()

for atdf in device_list:
    device_name = atdf.name.removesuffix(".atdf")
    source.write(next(ifdef) + device_name + "\n")
    source.write(f"#include \"mcu/{device_name}.hpp\"\n")
    device = open(header_path / (device_name + ".hpp"), "w")
    device.write("#pragma once\n")

source.write("#else\n#error Invalid or no MCU_NAME defined\n#endif")
