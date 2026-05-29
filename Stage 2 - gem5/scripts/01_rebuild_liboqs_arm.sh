#!/bin/bash
# 01_rebuild_liboqs_arm.sh
set -e
# BUILD=/home/user/liboqs/build-arm
BUILD=/home/user/liboqs/build-aarch64
SRC=/home/user/liboqs
echo "=== Rebuilding liboqs for ARM ==="
rm -rf $BUILD
mkdir -p $BUILD
cd $BUILD
cmake $SRC \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
  -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++ \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=OFF \
  -DOQS_USE_OPENSSL=OFF \
  -DOQS_BUILD_ONLY_LIB=ON \
  -DOQS_PERMIT_UNSUPPORTED_ARCHITECTURE=ON \
  -DCMAKE_INSTALL_PREFIX=$BUILD/install
make -j$(nproc)
make install
echo "=== Done ==="
file $BUILD/install/lib/liboqs.a


# not support time measurement
# apt-get install -y gcc-arm-linux-gnueabihf
# -DCMAKE_SYSTEM_PROCESSOR=arm \
# -DCMAKE_C_COMPILER=arm-linux-gnueabihf-gcc \
# -DCMAKE_CXX_COMPILER=arm-linux-gnueabihf-g++ \
# -DCMAKE_C_FLAGS="-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard" \


# apt-get install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

"""
This is a Bash script that cross-compiles the Open Quantum Safe liboqs cryptography library for an ARM Linux device.

Cross-compilation: Compile on one machine, but generate binaries for another architecture.
liboqs is a library containing:
- Kyber
- Dilithium
- Falcon
- SPHINCS+
- and other post-quantum cryptography algorithms

* source code:
  `/home/user/liboqs`
* build output:
  `/home/user/liboqs/build-arm`

cmake $SRC ---> Starts configuring the project using CMake. liboqs source code


## Cross-Compilation Settings
1. Target operating system = Linux.
2. Target CPU architecture = ARM.
3. Use the ARM cross-compiler for C code.
This compiler generates ARM binaries even if you're compiling on x86 Ubuntu/WSL.
4. Same thing for C++.

---

# Build Options
5. Optimize for speed/performance.
6. Build static libraries only.
Static libraries are common in embedded systems.
7. Disable OpenSSL dependency.
Useful for:
* embedded systems
* lightweight builds
* avoiding external crypto dependencies
8. Build only the library itself.
Skip:
* tests
* examples
* benchmarks
* tools
Makes compilation smaller/faster.
9. Allows building even if ARM is not officially validated/supported by liboqs.
Without this, CMake might refuse.

---

# ARM CPU Optimization Flags
10. These are ARM-specific compiler optimizations.
11. Compile for ARMv7-A CPUs.
Examples:
* Cortex-A7
* Cortex-A8
* Cortex-A9
12. Enable:
* NEON SIMD instructions
* hardware floating point unit
This improves performance for:
* crypto
* vector math
* signal processing
13. Use hardware floating-point calling conventions.
Faster than software floating point.
Requires compatible ARM system libraries.

---
# Installation Location
14. Install compiled library into:
/home/user/liboqs/build-arm/install

After installation you get something like:

text
install/
 ├── include/
 └── lib/
      └── liboqs.a

---

# Build
Compile using all CPU cores.

Example
* 8-core CPU → make -j8
Faster compilation.

---
# Install
Copies built files into the install directory.
# Verify the Output File
It helps confirm:
* library exists
* architecture type
* file format

# Overall Purpose
1. Clean previous build
2. Configure liboqs for ARM
3. Cross-compile it
4. Optimize for ARMv7 + NEON
5. Produce a static ARM library
6. Install it into a local folder

"""