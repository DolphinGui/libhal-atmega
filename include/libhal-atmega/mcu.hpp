#pragma once

#include "libhal-atmega/uart.hpp"
#include <cstdint>

namespace hal::atmega {

namespace uart_impl {

extern hal::atmega::uart* global_uart[];
extern const uint8_t max_uarts;

void _set_baud(uint8_t index, uint16_t baud, bool u2x) noexcept;
void _configure(uint8_t index, uint8_t b, uint8_t c) noexcept;
void _clear(uint8_t index) noexcept;
}  // namespace uart_impl

}  // namespace hal::atmega