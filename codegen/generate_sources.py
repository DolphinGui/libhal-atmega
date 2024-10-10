#!/usr/bin/python3

from atdf_parse import find_usarts
import sys


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
usarts = find_usarts(open(f"{sys.argv[1]}/atdf/{mcu_name}.atdf"))

source = open("generated_sources.hpp", "w")

source.write(
    """#include <cstdint>
#include <libhal-atmega/uart.hpp>
#include <libhal-atmega/mcu.hpp>
namespace hal::atmega::uart_impl{
void _set_baud(uint8_t index, uint16_t baud, bool u2x) noexcept {
switch (index){"""
)

for x, usart in enumerate(usarts):
    source.write(
        f"""case {x}:
if(u2x)
  (*(volatile uint8_t*){usart.ctrl_a.offset:#x}) &= ~(2);
else
  (*(volatile uint8_t*){usart.ctrl_a.offset:#x}) |= 2;\n"""
    )
    if usart.baud.size == 2:
        source.write(
            f"(*(volatile uint8_t*){usart.baud.offset+1:#x})=baud>>8;\n(*(volatile uint8_t*){usart.baud.offset:#x})=baud&0xff;\n"
        )
    else:
        source.write(
            f"(*(volatile uint8_t*){usart.baud.offset:#x})=baud>>8;\n(*(volatile uint8_t*){usart.baud2.offset:#x})=baud&0xff;\n"
        )
source.write(
    """
default: break;
}
}

volatile uint8_t* _get_b(uint8_t index){
switch (index){"""
)
for x, us in enumerate(usarts):
    source.write(
        f"""
case {x}:
return (volatile uint8_t*){us.ctrl_b.offset:#x};
"""
    )
source.write(
    """
default: __builtin_unreachable();
}
}

volatile uint8_t* _get_c(uint8_t index){
switch (index){"""
)
for x, us in enumerate(usarts):
    source.write(
        f"""
case {x}:
return (volatile uint8_t*){us.ctrl_c.offset:#x};
"""
    )
source.write(
    """
default: __builtin_unreachable();
}
}

volatile uint8_t* _get_data(uint8_t index){
switch (index){"""
)
for x, us in enumerate(usarts):
    source.write(
        f"""
case {x}:
return (volatile uint8_t*){us.data.offset:#x};
"""
    )
source.write(
    """
default: __builtin_unreachable();
}
}

"""
)

for x, usart in enumerate(usarts):
    source.write(
        usart_udre_template.format(
            usart.udre, index=x, ctrl_a=usart.ctrl_a.offset, data=usart.data.offset
        )
    )
    source.write(usart_rx_template.format(usart.rx, index=x, data=usart.data.offset))

source.write(
    f"uint8_t const max_uarts = {len(usarts)};\nhal::atmega::uart* global_uart[{len(usarts)}]={{}};\n"
)

source.write("}")
