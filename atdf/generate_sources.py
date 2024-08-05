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
    ctrl_d: Register | None = None
    baud2: Register | None = None
    udre: int = 0
    rx: int = 0


def to_register(node: ET.Element):
    return Register(
        node.attrib["name"],
        int(node.attrib["offset"], 0),
        int(node.attrib["size"], 0),
        int(node.attrib.get("mask", "0xFF"), 0),
    )


def find_usarts(root: ET.Element):
    # There's only ever one device in devices. No I don't know why either
    device = root.find("devices").find("device")
    modules = root.find("modules")

    usarts: list[USART] = []
    for mod in modules:
        if mod.attrib["name"] == "USART":
            for reg_group in mod.findall("register-group"):
                items = {}
                for reg in reg_group:
                    if re.match(r"UDR\d?", reg.attrib["name"]):
                        items["data"] = to_register(reg)
                    elif re.match(r"UCSR\d?A", reg.attrib["name"]):
                        items["ctrl_a"] = to_register(reg)
                    elif re.match(r"UCSR\d?B", reg.attrib["name"]):
                        items["ctrl_b"] = to_register(reg)
                    elif re.match(r"UCSR\d?C", reg.attrib["name"]):
                        items["ctrl_c"] = to_register(reg)
                    elif re.match(r"UCSR\d?D", reg.attrib["name"]):
                        items["ctrl_d"] = to_register(reg)
                    elif re.match(r"UBRR\d?L", reg.attrib["name"]):
                        items["baud2"] = to_register(reg)
                    elif re.match(r"UBRR\d?H?", reg.attrib["name"]):
                        items["baud"] = to_register(reg)
                usarts.append(USART(**items))
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

mcu_name = sys.argv[2]
atdf = open(f"{sys.argv[1]}/atdf/{mcu_name}.atdf")
tree = ET.parse(atdf)
root = tree.getroot()
usarts = find_usarts(root)

assert (
    root.find("./devices/device").attrib["architecture"] == "AVR8"
), "Incompatible device specified"
source = open("generated_sources.hpp", "w")

source.write("""#include <cstdint>
#include <libhal-atmega/uart.hpp>
#include <libhal-atmega/mcu.hpp>
namespace hal::atmega::uart_impl{
void _set_baud(uint8_t index, uint16_t baud, bool u2x) noexcept {
switch (index){""")

for x, usart in enumerate(usarts):
    source.write(f"""case {x}:
if(u2x)
  (*(volatile uint8_t*){usart.ctrl_a.offset:#x}) &= ~(2);
else
  (*(volatile uint8_t*){usart.ctrl_a.offset:#x}) |= 2;\n""")
    if usart.baud.size == 2:
        source.write(
            f"(*(volatile uint8_t*){usart.baud.offset+1:#x})=baud>>8;\n(*(volatile uint8_t*){usart.baud.offset:#x})=baud&0xff;\n"
        )
    else:
        source.write(
            f"(*(volatile uint8_t*){usart.baud.offset:#x})=baud>>8;\n(*(volatile uint8_t*){usart.baud2.offset:#x})=baud&0xff;\n"
        )
source.write("""
default: break;
}
}

volatile uint8_t* _get_b(uint8_t index){
switch (index){""")
for x, us in enumerate(usarts):
    source.write(f"""
case {x}:
return (volatile uint8_t*){us.ctrl_b.offset:#x};
""")
source.write("""
default: __builtin_unreachable();
}
}

volatile uint8_t* _get_c(uint8_t index){
switch (index){""")
for x, us in enumerate(usarts):
    source.write(f"""
case {x}:
return (volatile uint8_t*){us.ctrl_c.offset:#x};
""")
source.write("""
default: __builtin_unreachable();
}
}

volatile uint8_t* _get_data(uint8_t index){
switch (index){""")
for x, us in enumerate(usarts):
    source.write(f"""
case {x}:
return (volatile uint8_t*){us.data.offset:#x};
""")
source.write("""
default: __builtin_unreachable();
}
}

""")

for x, usart in enumerate(usarts):
    source.write(
        usart_udre_template.format(
            usart.udre, index=x, ctrl_a=usart.ctrl_a.offset, data=usart.data.offset
        )
    )
    source.write(usart_rx_template.format(usart.rx, index=x, data=usart.data.offset))

source.write(f"uint8_t const max_uarts = {len(usarts)};\nhal::atmega::uart* global_uart[{len(usarts)}]={{}};\n")

source.write("}")
