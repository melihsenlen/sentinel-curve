#ifndef SENTINEL_CURVE_MONITOR_HPP
#define SENTINEL_CURVE_MONITOR_HPP

#include <cstdint>
#include <string>


namespace sentinel {

struct Sample {
    std::uint64_t timestamp;
    double cpu;
    double memory;
};

Sample collectSample();
std::string to_csv(const Sample& sample);
}

#endif