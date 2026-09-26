#include "monitor.hpp"
#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
#include <string>
#include <cstdlib>
#include <filesystem>


int main(int argc, char* argv[]) {
    int interval_sec = 1;
    int duration_sec = -1;
    std::string output_file = "data.csv";

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if      (arg == "--interval" && i + 1 < argc) interval_sec = std::atoi(argv[++i]);
        else if (arg == "--duration" && i + 1 < argc) duration_sec = std::atoi(argv[++i]);
        else if (arg == "--output"   && i + 1 < argc) output_file  = argv[++i];
        else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            return 1;
        }
    }

    std::filesystem::path output_path(output_file);
    if (output_path.has_parent_path()) {
        std::error_code ec;
        std::filesystem::create_directories(output_path.parent_path(), ec);
        if (ec) {
            std::cerr << "Failed to create output directory: " << ec.message() << std::endl;
            return 1;
        }
    }

    std::ofstream out(output_file);
    if (!out.is_open()) {
        std::cerr << "Cannot open output file: " << output_file << std::endl;
        return 1;
    }

    out << "timestamp,cpu,memory\n";
    out.flush();

    int elapsed = 0;
    while (duration_sec < 0 || elapsed < duration_sec) {
        sentinel::Sample s = sentinel::collectSample();

        out << sentinel::to_csv(s) << "\n";
        out.flush();

        std::cout 
            << "Timestamp: " << s.timestamp
            << " | CPU: "    << s.cpu << "%"
            << " | Memory: " << s.memory << " MB"
            << std::endl;

        std::this_thread::sleep_for(std::chrono::seconds(interval_sec));
        if (duration_sec > 0) elapsed += interval_sec;
    }
    out.close();

    std::cout 
        << "Duration: "    << duration_sec
        << " | Interval: " << interval_sec
        << " | Saved: "    << output_file
        << std::endl;
    return 0;
}