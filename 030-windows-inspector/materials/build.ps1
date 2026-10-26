# SPDX-License-Identifier: MIT
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force build | Out-Null
# Execute no x64 Native Tools Command Prompt do Visual Studio 2022.
cl /nologo /std:c++17 /W4 /EHsc /MD /LD materials/benign.cpp /Febuild/benign.dll
if ($LASTEXITCODE -ne 0) {
    throw 'build DLL falhou'
}
cl /nologo /std:c++17 /W4 /EHsc /MD materials/fixture.cpp /Febuild/fixture.exe
if ($LASTEXITCODE -ne 0) {
    throw 'build alvo falhou'
}
cl /nologo /std:c++17 /W4 /EHsc /MD starter/wininspect.cpp /Febuild/wininspect.exe
if ($LASTEXITCODE -ne 0) {
    throw 'build starter falhou'
}
