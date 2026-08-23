#include "monitor.hpp"
#include <windows.h>
#include <chrono>
#include <string>
#include <sstream>

namespace sentinel {

double cpuUsage() {
    static FILETIME prev_idleTime = {0,0};
    static FILETIME prev_kernelTime = {0,0};
    static FILETIME prev_userTime = {0,0};

    FILETIME idleTime, kernelTime, userTime;
    if (!GetSystemTimes(&idleTime, &kernelTime, &userTime)) return 0.0;

    ULONGLONG idleDiff   = (reinterpret_cast<ULONGLONG&>(idleTime) - reinterpret_cast<ULONGLONG&>(prev_idleTime));
    ULONGLONG kernelDiff = (reinterpret_cast<ULONGLONG&>(kernelTime) - reinterpret_cast<ULONGLONG&>(prev_kernelTime));
    ULONGLONG userDiff   = (reinterpret_cast<ULONGLONG&>(userTime) - reinterpret_cast<ULONGLONG&>(prev_userTime));

    prev_idleTime   = idleTime;
    prev_kernelTime = kernelTime;
    prev_userTime   = userTime;

    ULONGLONG total = kernelDiff + userDiff;
    double cpu      = (total - idleDiff) * 100.0 / total;

    if (cpu < 0.0) cpu   = 0.0;
    if (cpu > 100.0) cpu = 100.0;
    return cpu;
}

double memoryUsage() {
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    if (!GlobalMemoryStatusEx(&memInfo)) return 0.0;

    DWORDLONG used = memInfo.ullTotalPhys - memInfo.ullAvailPhys;
    return static_cast<double>(used) / (1024 * 1024);
}

Sample collectSample() {
    Sample s;

    auto now = std::chrono::system_clock::now();
    s.timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();

    s.cpu = cpuUsage();
    s.memory = memoryUsage();
    return s;
}

std::string to_csv(const Sample& sample) {
    std::ostringstream ss;
    ss << sample.timestamp << ","
       << sample.cpu << ","
       << sample.memory;
    return ss.str();
}
}