#pragma once

#include "libhal-atmega/uart.hpp"
#include <cstdint>

namespace hal::atmega {

namespace uart_impl {

extern hal::atmega::uart* global_uart[];
extern const uint8_t max_uarts;

void _set_baud(uint8_t index, uint16_t baud, bool u2x) noexcept;
volatile uint8_t* _get_b(uint8_t index);
volatile uint8_t* _get_c(uint8_t index);
volatile uint8_t* _get_data(uint8_t index);
}  // namespace uart_impl

}  // namespace hal::atmega