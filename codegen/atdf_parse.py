import xml.etree.ElementTree as ET
from dataclasses import dataclass
import re


@dataclass
class Register:
    name: str
    offset: int
    size: int = 1
    mask: int = 0xFF



def to_register(node: ET.Element):
    return Register(
        node.attrib["name"],
        int(node.attrib["offset"], 0),
        int(node.attrib["size"], 0),
        int(node.attrib.get("mask", "0xFF"), 0),
    )


def is_valid_device(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root.find("./devices/device").attrib["architecture"] == "AVR8"


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

def parse_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    assert (
        root.find("./devices/device").attrib["architecture"] == "AVR8"
    ), "Incompatible device specified"
    return root

def find_usarts(file):
    root = parse_file(file)
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


@dataclass
class PIN:
    number: int
    pin_number: int
    port: str


def find_pins(file):
    root = parse_file(file)
    # There's only ever one device in devices. No I don't know why either
    device = root.find("devices").find("device")
    modules = root.find("modules")
