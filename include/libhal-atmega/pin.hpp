#pragma once

#include <cstdint>

namespace hal::atmega {
struct pin
{
  uint8_t port, pin;
};
}  // namespace hal::atmega