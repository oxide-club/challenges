// SPDX-License-Identifier: MIT
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <string>
#include <stdexcept>
#include <vector>
#include <cstdint>
#include <io.h>
#include <fcntl.h>
struct Owned {
    HANDLE h = nullptr;
    ~Owned() {
        if (h && h != INVALID_HANDLE_VALUE)
            CloseHandle(h);
    }
    void reset() {
        if (h && h != INVALID_HANDLE_VALUE)
            CloseHandle(h);
        h = nullptr;
    }
};
static void error(const char *api);
static std::string utf8(const std::wstring &s) {
    int n = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, s.c_str(), -1, nullptr, 0, nullptr,
                                nullptr);
    if (n <= 0)
        error("WideCharToMultiByte size");
    std::string r(static_cast<size_t>(n), '\0');
    if (WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, s.c_str(), -1, r.data(), n, nullptr,
                            nullptr) != n)
        error("WideCharToMultiByte conversion");
    r.pop_back();
    return r;
}
static std::string quote(const std::string &s) {
    std::string r = "\"";
    for (unsigned char c : s) {
        if (c == '\\' || c == '\"')
            r += '\\';
        if (c < 32) {
            char b[7];
            sprintf_s(b, "\\u%04x", c);
            r += b;
        } else
            r += c;
    }
    return r + '\"';
}
static void error(const char *api) {
    DWORD e = GetLastError();
    std::fprintf(stderr, "{\"api\":\"%s\",\"error\":%lu}\n", api, e);
    throw std::runtime_error(api);
}
static void emit(const std::string &s) {
    std::puts(s.c_str());
    std::fflush(stdout);
}
static void ack(int phase) {
    HANDLE input = GetStdHandle(STD_INPUT_HANDLE);
    ULONGLONG end = GetTickCount64() + 5000;
    std::string line;
    while (GetTickCount64() < end) {
        DWORD n = 0;
        if (!PeekNamedPipe(input, nullptr, 0, nullptr, &n, nullptr))
            error("PeekNamedPipe");
        if (n) {
            char c;
            DWORD got;
            if (!ReadFile(input, &c, 1, &got, nullptr) || got != 1)
                error("ReadFile");
            line += c;
            if (line.size() > 64)
                throw std::runtime_error("ACK longo");
            if (c == '\n') {
                if (line != "ACK " + std::to_string(phase) + "\n")
                    throw std::runtime_error("ACK inválido");
                return;
            }
        } else
            Sleep(1);
    }
    SetLastError(WAIT_TIMEOUT);
    error("ACK");
}
static DWORD WINAPI worker(void *p) {
    return WaitForSingleObject((HANDLE)p, INFINITE) == WAIT_OBJECT_0 ? 0 : 1;
}
int wmain(int argc, wchar_t **argv) {
    _setmode(_fileno(stdout), _O_BINARY);
    if (argc == 4 && std::wstring(argv[3]) != L"early") {
        std::fputs("modo inválido: use early\n", stderr);
        return 2;
    }
    if (argc < 3 || argc > 4) {
        std::fputs("fixture.exe SESSION ABSOLUTE_DLL [early]\n", stderr);
        return 2;
    }
#if !defined(_M_X64)
    std::fputs("{\"kind\":\"incompatible-environment\",\"message\":\"alvo requer Windows x64\"}\n",
               stderr);
    return 77;
#endif
    std::wstring session = argv[1];
    for (wchar_t c : session)
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || c == '-')) {
            std::fputs("sessão inválida\n", stderr);
            return 2;
        }
    if (session.empty() || session.size() > 64) {
        std::fputs("sessão deve conter 1–64 caracteres [a-z0-9-]\n", stderr);
        return 2;
    }
    wchar_t full[32768];
    DWORD len = GetFullPathNameW(argv[2], 32768, full, nullptr);
    if (!len || len >= 32768 || std::wstring(full) != argv[2]) {
        std::fputs("DLL exige caminho absoluto válido\n", stderr);
        return 2;
    }
    Owned stop, second, file, threads[2];
    HMODULE dll = nullptr;
    void *pages = nullptr;
    DWORD tids[2] = {};
    int status = 0;
    auto cleanup = [&]() {
        if (stop.h)
            SetEvent(stop.h);
        for (auto &t : threads) {
            if (t.h && WaitForSingleObject(t.h, 5000) != WAIT_OBJECT_0)
                TerminateProcess(GetCurrentProcess(), 1);
            t.reset();
        }
        if (dll) {
            if (!FreeLibrary(dll)) {
                std::fprintf(stderr, "{\"api\":\"FreeLibrary\",\"error\":%lu}\n", GetLastError());
                status = 1;
            } else
                dll = nullptr;
        }
        if (pages) {
            if (!VirtualFree(pages, 0, MEM_RELEASE)) {
                std::fprintf(stderr, "{\"api\":\"VirtualFree\",\"error\":%lu}\n", GetLastError());
                status = 1;
            } else
                pages = nullptr;
        }
        file.reset();
        second.reset();
        stop.reset();
    };
    try {
        std::string prefix =
            "{\"session\":" + quote(utf8(session)) +
            ",\"architecture\":\"x64\",\"pid\":" + std::to_string(GetCurrentProcessId());
        emit(
            prefix +
            ",\"phase\":0,\"ready\":true,\"handles\":[],\"tids\":[],\"module\":null,\"region\":null}");
        ack(0);
        if (argc == 4 && std::wstring(argv[3]) == L"early")
            return 23;
        stop.h = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        if (!stop.h)
            error("CreateEventW");
        second.h = CreateEventW(nullptr, FALSE, FALSE, nullptr);
        if (!second.h)
            error("CreateEventW");
        wchar_t tmp[MAX_PATH], name[MAX_PATH];
        DWORD temp_len = GetTempPathW(MAX_PATH, tmp);
        if (!temp_len)
            error("GetTempPathW");
        if (temp_len >= MAX_PATH) {
            SetLastError(ERROR_BUFFER_OVERFLOW);
            error("GetTempPathW length");
        }
        if (!GetTempFileNameW(tmp, L"oxc", 0, name))
            error("GetTempFileNameW");
        file.h = CreateFileW(name, GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING,
                             FILE_ATTRIBUTE_TEMPORARY | FILE_FLAG_DELETE_ON_CLOSE, nullptr);
        if (file.h == INVALID_HANDLE_VALUE) {
            DWORD saved = GetLastError();
            DeleteFileW(name);
            SetLastError(saved);
            error("CreateFileW");
        }
        dll = LoadLibraryW(full);
        if (!dll)
            error("LoadLibraryW");
        SYSTEM_INFO info;
        GetSystemInfo(&info);
        SIZE_T size = info.dwPageSize;
        pages = VirtualAlloc(nullptr, 3 * size, MEM_RESERVE, PAGE_NOACCESS);
        if (!pages)
            error("VirtualAlloc reserve");
        if (!VirtualAlloc((char *)pages + size, size, MEM_COMMIT, PAGE_READWRITE))
            error("VirtualAlloc RW");
        if (!VirtualAlloc((char *)pages + 2 * size, size, MEM_COMMIT, PAGE_READONLY))
            error("VirtualAlloc RO");
        for (int i = 0; i < 2; i++) {
            threads[i].h = CreateThread(nullptr, 0, worker, stop.h, 0, &tids[i]);
            if (!threads[i].h)
                error("CreateThread");
        }
        emit(
            prefix + ",\"phase\":1,\"ready\":true,\"tids\":[" + std::to_string(tids[0]) + "," +
            std::to_string(tids[1]) + "],\"module\":" + quote(utf8(full)) +
            ",\"handles\":[{\"id\":\"event-stop\",\"action\":\"create\"},{\"id\":\"event-spare\",\"action\":\"create\"},{\"id\":\"file-temp\",\"action\":\"create\",\"path\":" +
            quote(utf8(name)) + "}],\"region\":{\"base\":" + std::to_string((uintptr_t)pages) +
            ",\"size\":" + std::to_string(3 * size) + ",\"page_size\":" + std::to_string(size) +
            "}}");
        ack(1);
        cleanup();
        if (status)
            throw std::runtime_error("liberação de recursos falhou");
        emit(
            prefix +
            ",\"phase\":2,\"ready\":true,\"tids\":[],\"module\":null,\"region\":null,\"handles\":[{\"id\":\"event-stop\",\"action\":\"close\"},{\"id\":\"event-spare\",\"action\":\"close\"},{\"id\":\"file-temp\",\"action\":\"close\"}]}");
        ack(2);
    } catch (const std::exception &e) {
        std::fprintf(stderr, "fixture: %s\n", e.what());
        status = 1;
    }
    cleanup();
    return status;
}
