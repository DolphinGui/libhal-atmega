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
import os


required_conan_version = ">=2.0.14"


class libhal___platform___conan(ConanFile):
    name = "libhal-__platform__"
    license = "Apache-2.0"
    homepage = "https://libhal.github.io/libhal-__platform__"
    description = ("A collection of drivers and libraries for the __platform__ "
                   "series microcontrollers.")
    topics = ("microcontroller", "__platform__",)
    settings = "compiler", "build_type", "os", "arch"

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

    @property
    def _use_linker_script(self):
        return (self.options.platform == "profile1" or
                self.options.platform == "profile2")

    def add_linker_scripts_to_link_flags(self):
        platform = str(self.options.platform)
        self.cpp_info.exelinkflags = [
            "-L" + os.path.join(self.package_folder, "linker_scripts"),
            "-T" + os.path.join("libhal-__platform__", platform + ".ld"),
        ]

    def requirements(self):
        # Adds libhal and libhal-util as transitive headers, meaning library
        # consumers get the libhal and libhal-util headers downstream.
        bootstrap = self.python_requires["libhal-bootstrap"]
        bootstrap.module.add_library_requirements(self)

        # Replace with appropriate processor library
        self.requires("libhal-armcortex/[^4.0.0]")

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "libhal::__platform__")
        self.cpp_info.libs = ["libhal-__platform__"]

        if self.settings.os == "baremetal" and self._use_linker_script:
            self.add_linker_scripts_to_link_flags()

            self.buildenv_info.define("LIBHAL_PLATFORM",
                                      str(self.options.platform))
            self.buildenv_info.define("LIBHAL_PLATFORM_LIBRARY",
                                      "__platform__")

    def package_id(self):
        if self.info.options.get_safe("platform"):
            del self.info.options.platform
