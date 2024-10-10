# Copyright 2024 Khalil Estell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.15)

project(libhal-atmega LANGUAGES CXX)

find_package (Python3)

add_custom_command(
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/codegen/generate_sources.py ${CMAKE_CURRENT_SOURCE_DIR} ${MCU_NAME}
    DEPENDS codegen/generate_sources.py
    OUTPUT generated_sources.hpp
    COMMENT "Generating ATDF sources."
)

add_custom_command(
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/codegen/generate_headers.py ${CMAKE_CURRENT_SOURCE_DIR} ${MCU_NAME}
    DEPENDS codegen/generate_headers.py
    OUTPUT header.hpp
    COMMENT "Generating MCU headers."
)

add_custom_target(
  mcu_headers ALL
  COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/codegen/generate_headers.py ${CMAKE_CURRENT_SOURCE_DIR} ${MCU_NAME}
  DEPENDS codegen/generate_headers.py
)

include_directories(${CMAKE_BINARY_DIR})
include_directories(${CMAKE_BINARY_DIR}/generated_headers)

libhal_test_and_make_library(
  LIBRARY_NAME libhal-atmega

  SOURCES
  src/output_pin.cpp
  src/uart.cpp
  generated_sources.hpp

  TEST_SOURCES
  tests/output_pin.test.cpp
  tests/main.test.cpp

  PACKAGES
  libhal
  libhal-util
  ring-span-lite

  LINK_LIBRARIES
  libhal::libhal
  libhal::util
  nonstd::ring-span-lite
)
