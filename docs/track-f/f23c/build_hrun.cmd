@echo off
rem F23c (HPP-587): build the headless runner f23c_hrun.exe (one C++ file, Vulkan SDK 1.4.357.0 headers and loader
rem import library) and the two vertex shaders (glslangValidator of C:\kyty\tools\glslang). Not emulator code.
setlocal
if not defined PROCESSOR_ARCHITECTURE set "PROCESSOR_ARCHITECTURE=AMD64"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d C:\kyty\f287\f23c
clang-cl /nologo /O2 /EHsc /std:c++17 /W3 /I C:\VulkanSDK\1.4.357.0\Include f23c_hrun.cpp /Fe:f23c_hrun.exe /link C:\VulkanSDK\1.4.357.0\Lib\vulkan-1.lib || exit /b 1
C:\kyty\tools\glslang\bin\glslangValidator.exe -V --target-env vulkan1.3 -o work\vs_tri.spv vs_tri.vert || exit /b 1
C:\kyty\tools\glslang\bin\glslangValidator.exe -V --target-env vulkan1.3 -o work\vs_diamond.spv vs_diamond.vert || exit /b 1
echo BUILD OK
