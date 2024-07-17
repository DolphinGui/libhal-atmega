#include <libhal-atmega328p/uart.hpp>
#include <string_view>

volatile int a;
void application()
{
  std::array<uint8_t, 64> in{}, out{};
  auto uart = hal::atmega328p::uart(in, out);
  std::string_view str = "Hello World!\n\r";
  uart.write({ reinterpret_cast<const uint8_t*>(str.data()), str.length() });
  // idle so that avrsim does not prematurely die
  while(true){
    a = 12;
  }
}