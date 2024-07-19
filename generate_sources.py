#!/usr/bin/python3

import xml.etree.ElementTree as ET
from dataclasses import dataclass
import re
import sys

@dataclass
class Register:
    name: str
    offset: int
    size: int = 1
    mask: int = 0xFF


@dataclass
class USART:
    data: Register
    ctrl_a: Register
    ctrl_b: Register
    ctrl_c: Register
    baud: Register
    # baud2: Register
    udre: int = 0
    rx: int = 0


def to_register(node: ET.Element, reg_name: str):
    assert re.match(
        reg_name, node.attrib["name"]
    ), f'Register {node.attrib["name"]} does not match {reg_name}'
    return Register(
        node.attrib["name"],
        int(node.attrib["offset"], 0),
        int(node.attrib["size"], 0),
        int(node.attrib.get("mask", "0xFF"), 0),
    )


def find_usarts(root):
    # There's only ever one device in devices. No I don't know why either
    device = root.find("devices").find("device")
    modules = root.find("modules")

    usarts: list[USART] = []
    for mod in modules:
        if mod.attrib["name"] == "USART":
            for reg_group in mod.findall("register-group"):
                # This is horribly fragile. I hate this. It's probably fine since
                # they reuse IP for the chips, probably, but still.
                # If they ever change how they order things, this breaks.
                ubr = (
                    [reg_group[4]]
                    if len(reg_group) == 5
                    else [reg_group[4], [reg_group[5]]]
                )
                usarts.append(
                    USART(
                        to_register(reg_group[0], "UDR\\d?"),
                        to_register(reg_group[1], "UCSR\\d?A"),
                        to_register(reg_group[2], "UCSR\\d?B"),
                        to_register(reg_group[3], "UCSR\\d?C"),
                        *ubr,
                    )
                )
    interrupts = device.find("interrupts")
    if len(usarts) == 1:
        ud = re.compile("USART[01]?_UDRE")
        rx = re.compile("USART[01]?_RX")
        for interrupt in interrupts:
            if ud.match(interrupt.attrib["name"]):
                usarts[0].udre = int(interrupt.attrib["index"])
            elif rx.match(interrupt.attrib["name"]):
                usarts[0].rx = int(interrupt.attrib["index"])
        if usarts[0].udre == 0 or usarts[0].rx == 0:
            return None
    else:
        for i, usart in enumerate(usarts):
            usart.udre = int(
                interrupts.find(f'./*[@name="USART{i}_UDRE"]').attrib["index"]
            )
            rx = interrupts.find(f'./*[@name="USART{i}_RX"]')
            # literally only atmega162 uses RXC
            if rx is None:
                rx = interrupts.find(f'./*[@name="USART{i}_RXC"]')
            usart.rx = int(rx.attrib["index"])
    return usarts


# Let's assume they won't be disgusting and change up the bit positions of each register
usart_udre_template = """
extern "C" void __vector_{0}(void) noexcept
  __attribute__((__signal__, __used__, __externally_visible__)) ;
void __vector_{0}(void) noexcept {{
  auto& uart = *global_uart[{index}];
  if (uart.m_tx.empty()) {{
    (*(volatile uint8_t*){ctrl_a:#x}) &= ~(1 << 5);
  }} else {{
    (*(volatile uint8_t*){data:#x}) = uart.m_tx.pop_front();
  }}
}}
"""

usart_rx_template = """
extern "C" void __vector_{0}(void) noexcept
  __attribute__((__signal__, __used__, __externally_visible__)) ;
void __vector_{0}(void) noexcept {{
  auto& uart = *global_uart[{index}];
  if (uart.m_rx.full()) {{
    uart.overwritten = true;
    uart.m_rx.pop_front();
  }}
  uint8_t data = (*(volatile uint8_t*){data:#x});
  uart.m_rx.push_back(data);
}}
"""

# header = """
# namespace libhal::
# """

mcu_name = sys.argv[2]
atdf = open(f"{sys.argv[1]}/atdf/{mcu_name}.atdf")
tree = ET.parse(atdf)
root = tree.getroot()
usarts = find_usarts(root)

assert root.find("./devices/device").attrib["architecture"] == "AVR8", "Incompatible device specified"
f = open("generated_sources.cpp", "w")
f.write(f"""#include <cstdint>
        #include <libhal-atmega/uart.hpp>
        namespace hal::{mcu_name.lower()}{{ 
        hal::atmega::uart* global_uart[{len(usarts)}] = {{}};
          """)

for x, usart in enumerate(usarts):
    f.write(
        usart_udre_template.format(
            usart.udre, index=x, ctrl_a=usart.ctrl_a.offset, data=usart.data.offset
        )
    )
    f.write(usart_rx_template.format(usart.rx, index=x, data=usart.data.offset))

f.write('}')