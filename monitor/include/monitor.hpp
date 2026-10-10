#ifndef SENTINEL_HPP
#define SENTINEL_HPP

#include <cstdint>
#include <string>


namespace sentinel {

struct Sample {
    std::uint64_t timestamp;
    double cpu;
    double memory;
};

Sample sample();
std::string csv(const Sample& sample);
}

#endif