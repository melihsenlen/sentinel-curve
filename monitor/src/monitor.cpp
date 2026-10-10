#include "monitor.hpp"
#include <windows.h>
#include <chrono>
#include <string>
#include <sstream>


namespace sentinel {

double cpuUsage() {
    static FILETIME prevIdle   = {0, 0};
    static FILETIME prevKernel = {0, 0};
    static FILETIME prevUser   = {0, 0};

    FILETIME idle, kernel, user;
    if (!GetSystemTimes(&idle, &kernel, &user)) return 0;

    ULONGLONG diffIdle   = (reinterpret_cast<ULONGLONG&>(idle) - reinterpret_cast<ULONGLONG&>(prevIdle));
    ULONGLONG diffKernel = (reinterpret_cast<ULONGLONG&>(kernel) - reinterpret_cast<ULONGLONG&>(prevKernel));
    ULONGLONG diffUser   = (reinterpret_cast<ULONGLONG&>(user) - reinterpret_cast<ULONGLONG&>(prevUser));

    prevIdle   = idle;
    prevKernel = kernel;
    prevUser   = user;

    ULONGLONG total = diffKernel + diffUser;
    if (total == 0) return 0;

    double cpu = (static_cast<double>(total) - diffIdle) * 100.0 / total;

    if (cpu < 0)   cpu = 0;
    if (cpu > 100) cpu = 100;
    return cpu;
}

double memoryUsage() {
    MEMORYSTATUSEX memory;
    memory.dwLength = sizeof(MEMORYSTATUSEX);
    if (!GlobalMemoryStatusEx(&memory)) return 0;

    DWORDLONG used = memory.ullTotalPhys - memory.ullAvailPhys;
    return static_cast<double>(used) / (1024 * 1024);
}

Sample sample() {
    Sample s;

    auto now = std::chrono::system_clock::now();
    s.timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();

    s.cpu = cpuUsage();
    s.memory = memoryUsage();
    return s;
}

std::string csv(const Sample& sample) {
    std::ostringstream ss;
    ss << sample.timestamp << ","
       << sample.cpu << ","
       << sample.memory;
    return ss.str();
}
}