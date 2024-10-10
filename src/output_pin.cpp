// Copyright 2024 Khalil Estell
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <avr/io.h>
#include <libhal-atmega/output_pin.hpp>
#include <libhal/error.hpp>
#include <libhal/units.hpp>

namespace {
volatile uint8_t& portx(uint8_t p)
{
  switch (p) {
    case 0:
      return PORTB;
    case 1:
      return PORTC;
    case 2:
      return PORTD;
    default:
      __builtin_unreachable();
  }
}

volatile uint8_t& ddxn(uint8_t p)
{
  switch (p) {
    case 0:
      return DDRB;
    case 1:
      return DDRC;
    case 2:
      return DDRD;
    default:
      __builtin_unreachable();
  }
}
volatile uint8_t& pinx(uint8_t p)
{
  switch (p) {
    case 0:
      return PINB;
    case 1:
      return PINC;
    case 2:
      return PIND;
    default:
      __builtin_unreachable();
  }
}
}  // namespace

namespace hal::atmega {
output_pin::output_pin(pin p)
  : port(p.port)
{
  pin_mask = 1 << p.pin;
}

void output_pin::driver_configure(const settings& options)
{
  open_drain = options.open_drain;
  if (open_drain) {
    ddxn(port) |= pin_mask;
    // I have no idea what pin_resistor is even supposed to mean. Probably makes
    // more sense on ARM or something.
    if (options.resistor != pin_resistor::pull_down)
      throw hal::operation_not_supported(this);
  } else {
    ddxn(port) &= ~pin_mask;
  }
}

void output_pin::driver_level(bool level)
{
  if (level)
    portx(port) |= pin_mask;
  else
    portx(port) &= ~pin_mask;
}

bool output_pin::driver_level()
{
  return pinx(port) & pin_mask;
}
}  // namespace hal::atmega
