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

#include <libhal-__platform__/output_pin.hpp>
#include <libhal-armcortex/dwt_counter.hpp>
#include <libhal-util/steady_clock.hpp>

void application()
{
  using namespace hal::literals;
  // TODO(libhal-target): Set the correct frequency and output pin driver
  hal::cortex_m::dwt_counter clock(1.0_MHz);
  hal::__platform__::output_pin led;

  while (true) {
    using namespace std::chrono_literals;
    led.level(false);
    hal::delay(clock, 200ms);
    led.level(true);
    hal::delay(clock, 200ms);
  }
}
