@echo off
rem F24a (HPP-658): pp_f24a.py inside the vcvars64 environment. Usage: pp_f24a.cmd <base|after|compare>
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
python C:/kyty/f287/f24a/pp_f24a.py %1
