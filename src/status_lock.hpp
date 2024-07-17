#pragma once

#include <cstdint>
#include <avr/interrupt.h>
#include <util/atomic.h>

namespace hal::atmega328p {
// A lock that prevents interrupts while running while in scope
struct slock
{
  inline slock() noexcept
  {
    reg = SREG;
    cli();
  }

  inline ~slock()
  {
    SREG = reg;
  }

  uint8_t reg;
};

}  // namespace hal::atmega328p