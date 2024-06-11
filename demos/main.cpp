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

// Replace with the correct processor includes
#include <libhal-__platform__/output_pin.hpp>
#include <libhal-armcortex/dwt_counter.hpp>
#include <libhal-armcortex/system_control.hpp>
#include <libhal-exceptions/control.hpp>
#include <libhal-util/steady_clock.hpp>

// Application function must be implemented by one of the compilation units
// (.cpp) files.
extern void application();

[[noreturn]] void terminate_handler() noexcept
{
  using namespace std::chrono_literals;
  using namespace hal::literals;
  // Replace this with something that makes sense...
  hal::cortex_m::dwt_counter clock(12.0_MHz);
  hal::__platform__::output_pin led;

  while (true) {
    led.level(false);
    hal::delay(clock, 100ms);
    led.level(true);
    hal::delay(clock, 100ms);
    led.level(false);
    hal::delay(clock, 100ms);
    led.level(true);
    hal::delay(clock, 1000ms);
  }
}

int main()
{
  // Add system initialization code here such as changing system clock speed.
  // Add necessary code here or delete this and the comment above...

  // Set terminate routine...
  hal::set_terminate(terminate_handler);

  // Run application
  application();

  // Reset the device if it gets here
  hal::cortex_m::reset();  // Replace with something that resets the device
  return 0;
}
