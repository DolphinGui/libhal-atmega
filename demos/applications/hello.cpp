#include <libhal-atmega/uart.hpp>
#include <string_view>
#include "mcu/io.hpp"

volatile uint16_t a;
void application()
{
  std::array<uint8_t, 64> in{}, out{};
  auto uart = hal::atmega::uart(in, out);
  uart.configure({});
  std::string_view str = "Hello World!\n\r";
  uart.write({ reinterpret_cast<const uint8_t*>(str.data()), str.length() });
  std::array<uint8_t, 16> string = {};
  while (true) {
    a = a + 1;
    if (a == 0) {
      auto n = uart.read(string);
      if (n.data.size() != 0)
        uart.write(n.data);
    }
  }
}
