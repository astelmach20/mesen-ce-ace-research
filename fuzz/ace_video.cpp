#include <iostream>
#include <filesystem>
#include <memory>
#include <exception>

#include "include/AceHarness.hpp"
#include "include/Payload6502.hpp"
#include "include/FrameExporter.hpp"

namespace mesen::video {

class ContinuousVideoRecorder {
public:
    ContinuousVideoRecorder(std::filesystem::path rom_path, std::filesystem::path output_dir)
        : m_harness(std::move(rom_path)), m_output_dir(std::move(output_dir)) {}

    bool record_full_sequence() {
        std::filesystem::create_directories(m_output_dir);

        if (!m_harness.initialize()) {
            std::cerr << "[Recorder] Harness initialization failed.\n";
            return false;
        }

        uint32_t frame_index = 0;
        uint32_t last_captured_frame = 0;

        auto record_frames = [&](uint32_t frame_count) {
            uint32_t target_frame = interop::GetTimingInfo(8).FrameCount + frame_count;
            while (interop::GetTimingInfo(8).FrameCount < target_frame) {
                uint32_t current_fc = interop::GetTimingInfo(8).FrameCount;
                if (current_fc != last_captured_frame) {
                    last_captured_frame = current_fc;
                    char filename[256];
                    snprintf(filename, sizeof(filename), "frame_%05u.ppm", frame_index++);
                    gfx::FrameExporter::export_ppm(m_output_dir / filename);
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        };

        std::cout << "[Recorder] Phase 1: Recording Title Screen (120 frames)...\n";
        record_frames(120);

        auto payload = ace::Payload6502::create_rainbow_visual_routine();
        m_harness.inject_vector_and_payload(payload);

        std::cout << "[Recorder] Phase 2: Transitioning to Gameplay Mode...\n";
        int guard = 0;
        while (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::OPERMODE) != 1 && guard++ < 600) {
            DebugControllerState start_state{};
            start_state.Start = true;
            interop::SetInputOverrides(0, start_state);
            record_frames(1);
            DebugControllerState release_state{};
            interop::SetInputOverrides(0, release_state);
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        }

        std::cout << "[Recorder] Phase 3: Recording Baseline World 1-1 (120 frames)...\n";
        record_frames(120);

        if (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::PAUSE_FLAG) & 0x01) {
            nes::MemoryAccessor::write8(nes::MemoryDomain::Ram, nes::addresses::PAUSE_FLAG, 0x00);
        }

        std::cout << "[Recorder] Phase 4: Recording Player Input & Spawner Trigger (300 frames max)...\n";
        DebugControllerState walk_state{};
        walk_state.Right = true;
        walk_state.A = true;
        interop::SetInputOverrides(0, walk_state);

        for (int f = 0; f < 300; ++f) {
            record_frames(1);
            bool slot_found = false;
            for (int s = 0; s < 6; ++s) {
                if (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::ENEMY_SLOT_FLAG_BASE + s) != 0) {
                    slot_found = true;
                    break;
                }
            }
            if (slot_found) break;
        }

        DebugControllerState release_state{};
        interop::SetInputOverrides(0, release_state);

        std::cout << "[Recorder] Phase 5: Recording Active ACE Rainbow Cycle (360 frames)...\n";
        record_frames(360);

        std::cout << "[Recorder] Done. Captured " << frame_index << " frames to " << m_output_dir << "\n";
        return true;
    }

private:
    ace::AceHarness m_harness;
    std::filesystem::path m_output_dir;
};

} // namespace mesen::video

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <path_to_smb1_rom> [output_frame_dir]\n";
        return 2;
    }

    try {
        std::filesystem::path rom_path = argv[1];
        std::filesystem::path output_dir = (argc >= 3) ? argv[2] : "/tmp/ace_frames";

        mesen::video::ContinuousVideoRecorder recorder(rom_path, output_dir);
        return recorder.record_full_sequence() ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << "[Fatal Exception] " << e.what() << "\n";
        return 1;
    }
}
