#include <iostream>
#include <filesystem>
#include <string_view>
#include <exception>

#include "include/AceHarness.hpp"
#include "include/Payload6502.hpp"
#include "include/FrameExporter.hpp"

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <path_to_smb1_rom> [output_proof_dir]\n";
        return 2;
    }

    try {
        std::filesystem::path rom_path = argv[1];
        std::filesystem::path proof_dir = (argc >= 3) ? argv[2] : "docs/assets/ace-proof";

        std::filesystem::create_directories(proof_dir);

        std::cout << "====================================================\n";
        std::cout << "  MesenCE SMB1 In-Game ACE Verification Harness    \n";
        std::cout << "====================================================\n";

        mesen::ace::AceHarness harness(rom_path);

        if (!harness.initialize()) {
            std::cerr << "[Error] Initialization failed.\n";
            return 1;
        }

        auto payload = mesen::ace::Payload6502::create_instant_win_routine();
        std::cout << "[Info] Payload: " << payload.description() << " (" << payload.size() << " bytes)\n";

        harness.inject_vector_and_payload(payload);
        mesen::gfx::FrameExporter::export_ppm(proof_dir / "01_title_screen.ppm");

        std::cout << "[Info] Advancing to gameplay mode...\n";
        if (!harness.advance_to_gameplay()) {
            std::cerr << "[Error] Failed to reach gameplay mode.\n";
            return 1;
        }

        mesen::gfx::FrameExporter::export_ppm(proof_dir / "02_game_start.ppm");

        std::cout << "[Info] Running ACE verification loop...\n";
        auto result = harness.run_verification();

        mesen::gfx::FrameExporter::export_ppm(proof_dir / "03_after_ace_rainbow.ppm");
        harness.wait_frames(16);
        mesen::gfx::FrameExporter::export_ppm(proof_dir / "04_after_ace_cycled.ppm");

        std::cout << "----------------------------------------------------\n";
        std::cout << " Result: " << (result.success ? "SUCCESS [ACE EXECUTED IN-GAME]" : "FAILED") << "\n";
        std::cout << " Marker ($07FF): 0x" << std::hex << (int)result.marker_value << std::dec << "\n";
        std::cout << " Active Enemy Slot: " << result.active_enemy_slot << "\n";
        std::cout << " Details: " << result.details << "\n";
        std::cout << " Proof directory: " << proof_dir << "\n";
        std::cout << "====================================================\n";

        return result.success ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << "[Fatal Exception] " << e.what() << "\n";
        return 1;
    }
}
