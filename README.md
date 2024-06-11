# libhal-__platform__

[![✅ Checks](https://github.com/libhal/libhal-__platform__/actions/workflows/ci.yml/badge.svg)](https://github.com/libhal/libhal-__platform__/actions/workflows/ci.yml)
[![Coverage](https://libhal.github.io/libhal-__platform__/coverage/coverage.svg)](https://libhal.github.io/libhal-__platform__/coverage/)
[![GitHub stars](https://img.shields.io/github/stars/libhal/libhal-__platform__.svg)](https://github.com/libhal/libhal-__platform__/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/libhal/libhal-__platform__.svg)](https://github.com/libhal/libhal-__platform__/network)
[![GitHub issues](https://img.shields.io/github/issues/libhal/libhal-__platform__.svg)](https://github.com/libhal/libhal-__platform__/issues)

Platform library for __platform__ series of devices.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

---

## Making a new platform driver (Delete section below)

Use [libhal/libhal-lpc40](https://github.com/libhal/libhal-lpc40/) as an
example of the sections a README should have.

To make your own libhal library:

1. Press the green "Use this Template" button then.
2. Press the "Create a new repository".
3. Name it `libhal-<insert_platform_name>` and replace `<insert_platform_name>`
   with the name of the device's family. For exmaple, if you want to make a
   library for the stm32f103 which is in the stm32f1 series of MCUs then call
   it `libhal-stm32f1`.
4. Choose where to put the repo under.
5. Go to `settings` > `Pages` > `Build and deployment` > `Source` and set the
   source to `Github Actions`.
6. Go to `Pull Requests` and merge the library rename pull request.
7. Done!

## About the libhal-platform template

The `libhal-__platform__` repository is a template for creating platform
libraries in the libhal ecosystem. It provides a structured layout and a set of files to help you get started with creating your own platform library.

## .github/workflows

This directory contains GitHub Actions workflow files for continuous integration
(CI) and other automated tasks. The workflows currently included are:

- `ci.yml`: This workflow runs the CI pipeline, which includes
  building the project, running tests, and deploying the library to the
  `libhal-trunk` package repository.
- `take.yml`: This workflow is responsible for the "take" action, which assigns
  commits to
- `deploy-version.yml`: A helper CI workflow that builds the library for each
  target architecture/os/etc.
- `0.0.1.yml`: A launch file. This file is used to manually release a version
  of the project via the "work dispatch" function of github actions.
- `update_name.yml`: This workflow updates the name of the repository when it's
  used as a template for a new repository.

## conanfile.py

This is a [Conan](https://conan.io/) recipe file. Conan is a package manager for
C and C++ that helps manage dependencies in your project. This file defines how
Conan should build your project and its dependencies.

### Update topics

Add more tags to the `topics` attribute of your the file.

### Setting the processor library

The default processor library used is `libhal-armcortex`. Replace the follow
code block in the file with the appropriate processor library.

```python
# Replace with appropriate processor library
self.requires("libhal-armcortex/[^3.0.2]")
```

### Adding available platforms

```python
options = {
    "platform": [
        "profile1",
        "profile2",
        "not-me"
    ],
}
```

Replace `"profile1"` and `"profile2"` with the exact names of each platform in
the platform's family. For example, in the `stm32f1` family of microcontrollers
there are `stm32f100`, `stm32f101`, `stm32f102`, `stm32f103`, `stm32f105`, and
`stm32f107`.

Keep `default_options` as it is.

## linker_scripts/libhal-__platform__

This directory contains linker scripts for different configurations of the
platform. Each linker script specifies how the linker should arrange the
sections of the program in memory.

Each platform specified in the `conanfile.py` file must have a corresponding
linker script in this directory. For example, the `stm32f1` family of
microcontrollers would have `stm32f100.ld`, `stm32f101.ld`, `stm32f102.ld`,
`stm32f103.ld`, `stm32f105.ld`, and `stm32f107.ld`.

For details of how these linker scripts should be composed in your library,
please see the documentation for the processor library used for the platform.
Usually this information is put in the processor library's README.md.

## conan/profiles

This directory contains Conan profiles for different configurations of the
platform. Each profile specifies a set of settings and options that Conan should
use when building the project.

Each platform specified in the `conanfile.py` file must have a corresponding
profile in this directory. Using the `stm32f1` family as an example, you will
have the following profiles: `stm32f100`, `stm32f101`, `stm32f102`, `stm32f103`,
`stm32f105`, `stm32f107`.

For details of how these profiles should be composed in your library,
please see the documentation for the processor library used for the platform.
Usually this information is put in the processor library's README.md.

## datasheets

This directory is intended for storing data sheets related to the platform that
the library is being built for. It currently contains a placeholder file,
`placeholder.txt`.

Many data sheets are subject to copyright and that must be considered when
adding the data sheet to a libhal repo. If the data sheet cannot be
redistributed on the repo for copyright and/or license reasons, then a markdown
file with a link to the data sheet (and potentially mirrors of it) is an
acceptable alternative.

## demos

This directory contains demonstration applications showing how to use the
platform library. It includes:

- `applications/blinker.cpp`: A sample application demonstrating usage of the
  platform library.
- `main.cpp`: The main entry point for the demo applications.

## include/libhal-__platform__

This directory contains the header files for the platform library. It currently
includes `output_pin.hpp`, which is a placeholder for the main header file of
your platform library.

## src

This directory contains the source files for the platform library. It currently
includes `output_pin.cpp`, which is a placeholder for drivers for this platform
library.

## test_package

This directory contains a test package for the Conan recipe. It includes a
simple application that uses the platform library, which helps verify that the
Conan recipe is working correctly.

## tests

This directory contains tests for the platform library. It includes:

- `__platform__.test.cpp`: A placeholder for tests for the platform library.
- `main.test.cpp`: The main entry point for the tests.

Remember to replace all instances of `__platform__` with the actual name of the
platform that your library is being built for.
