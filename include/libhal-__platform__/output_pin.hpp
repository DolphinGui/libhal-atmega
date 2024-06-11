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

#pragma once

#include <libhal/output_pin.hpp>

namespace hal::__platform__ {  // NOLINT
class output_pin : public hal::output_pin
{
public:
  /// TODO: Update constructor
  output_pin() = default;

private:
  // Add constructor
  void driver_configure(const settings& p_settings) override;
  void driver_level(bool p_high) override;
  bool driver_level() override;
};
}  // namespace hal::__platform__
