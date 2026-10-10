#include "monitor.hpp"
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
#include <string>
#include <cstdlib>
#include <filesystem>


int main(int argc, char* argv[]) {
    int interval = 1;
    int duration = -1;
    std::string output = "data.csv";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if      (arg == "--interval" && i + 1 < argc) interval = std::atoi(argv[++i]);
        else if (arg == "--duration" && i + 1 < argc) duration = std::atoi(argv[++i]);
        else if (arg == "--output"   && i + 1 < argc) output  = argv[++i];
        else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            return 1;
        }
    }

    if (interval < 1) {
        std::cerr << "--interval must be a positive integer" << std::endl;
        return 1;
    }

    std::filesystem::path path(output);
    if (path.has_parent_path()) {
        std::error_code error;
        std::filesystem::create_directories(path.parent_path(), error);
        if (error) {
            std::cerr << "Failed to create output directory: " << error.message() << std::endl;
            return 1;
        }
    }

    std::ofstream out(output);
    if (!out.is_open()) {
        std::cerr << "Cannot open output file: " << output << std::endl;
        return 1;
    }

    out << "timestamp,cpu,memory\n";
    out.flush();

    sentinel::sample(); // primes the cpu counters, result discarded

    int elapsed = 0;
    while (duration < 0 || elapsed < duration) {
        std::this_thread::sleep_for(std::chrono::seconds(interval));
        if (duration > 0) elapsed += interval;

        sentinel::Sample s = sentinel::sample();

        out << sentinel::csv(s) << "\n";
        out.flush();

        std::cout 
            << "Timestamp: " << s.timestamp
            << " | CPU: "    << s.cpu << "%"
            << " | Memory: " << s.memory << " MB"
            << std::endl;
    }
    out.close();

    std::cout 
        << "Duration: "    << duration
        << " | Interval: " << interval
        << " | Saved: "    << output
        << std::endl;
    return 0;
}