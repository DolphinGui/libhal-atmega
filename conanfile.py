#!/usr/bin/python
#
# Copyright 2024 Khalil Estell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from conan import ConanFile

from conan.tools.cmake import  CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv

required_conan_version = ">=2.0.14"

class libhal_atmega328p_conan(ConanFile):
    name = "libhal-atmega"
    license = "Apache-2.0"
    homepage = "https://libhal.github.io/libhal-atmega328p"
    description = ("A collection of drivers and libraries for the ATMega "
                   "series microcontrollers.")
    topics = ("microcontroller", "atmega",)
    settings = "compiler", "build_type", "os", "arch", "mcu", "clock"

    python_requires = "libhal-bootstrap/[^2.0.0]"
    python_requires_extend = "libhal-bootstrap.library"

    options = {
        "platform": [
            "profile1",
            "profile2",
            "ANY"
        ],
    }

    default_options = {
        "platform": "ANY",
    }

    def generate(self):
        virt = VirtualBuildEnv(self)
        virt.generate()
        tc = CMakeToolchain(self)
        tc.variables["MCU_NAME"] = self.settings.mcu
        tc.variables["CLOCK"] = self.settings.clock
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def requirements(self):
        bootstrap = self.python_requires["libhal-bootstrap"]
        bootstrap.module.add_library_requirements(self)
        self.requires("ring-span-lite/[^0.7.0]", transitive_headers=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "libhal::atmega328p")
        self.cpp_info.libs = ["libhal-atmega328p"]

        if self.settings.os == "baremetal":
            self.buildenv_info.define("LIBHAL_PLATFORM",
                                      str(self.options.platform))
            self.buildenv_info.define("LIBHAL_PLATFORM_LIBRARY",
                                      "atmega328p")

    def package_id(self):
        if self.info.options.get_safe("platform"):
            del self.info.options.platform
