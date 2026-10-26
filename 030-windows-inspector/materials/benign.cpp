// SPDX-License-Identifier: MIT
#include <windows.h>
extern "C" __declspec(dllexport) int oxide_fixture_version() { return 1; }
BOOL WINAPI DllMain(HINSTANCE, DWORD, LPVOID) { return TRUE; }
