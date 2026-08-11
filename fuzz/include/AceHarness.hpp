#pragma once

#include <filesystem>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include <iostream>

#include "MesenApi.hpp"
#include "NesMemory.hpp"
#include "Payload6502.hpp"
#include "FrameExporter.hpp"

namespace mesen::ace {

struct ExecutionResult {
    bool success{false};
    uint8_t marker_value{0x00};
    uint32_t active_enemy_slot{0};
    std::string details;
};

class AceHarness {
public:
    explicit AceHarness(std::filesystem::path rom_path)
        : m_rom_path(std::move(rom_path)) {}

    ~AceHarness() {
        shutdown();
    }

    bool initialize() {
        std::filesystem::path home = "/tmp/mesen_fuzz_home";
        std::filesystem::create_directories(home);

        interop::InitDll();
        interop::InitializeEmu(home.c_str(), nullptr, nullptr, false, true, true, true);
        interop::SetEmulationFlag(0x04 /* MaximumSpeed */, true);

        NesConfig nes_config{};
        nes_config.Port1.Type = ControllerType::NesController;
        nes_config.Port2.Type = ControllerType::NesController;
        nes_config.AutoConfigureInput = true;
        interop::SetNesConfig(nes_config);

        std::string rom_str = m_rom_path.string();
        if (!interop::LoadRom(rom_str.data(), nullptr)) {
            std::cerr << "[AceHarness] Failed to load ROM: " << m_rom_path << std::endl;
            return false;
        }

        std::cout << "[AceHarness] ROM successfully loaded: " << m_rom_path.filename() << std::endl;
        return true;
    }

    void wait_frames(uint32_t count) {
        uint32_t target = interop::GetTimingInfo(8).FrameCount + count;
        while (interop::GetTimingInfo(8).FrameCount < target) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        }
    }

    void inject_vector_and_payload(const Payload6502& payload) {
        wait_frames(180);

        // Pause emulator safely before touching debugger hooks
        interop::Pause();
        interop::InitializeDebugger();

        std::cout << "[AceHarness] Unmasking enemy spawner ($41F4 -> 0xFF)..." << std::endl;
        nes::MemoryAccessor::write8(nes::MemoryDomain::PrgRom, nes::addresses::PRG_SPAWNER_MASK_OFFSET, nes::addresses::UNMASKED_SPAWNER_VAL);

        std::cout << "[AceHarness] Patching World 1-1 Goomba ID ($1F05 -> 0x85)..." << std::endl;
        nes::MemoryAccessor::write8(nes::MemoryDomain::PrgRom, nes::addresses::PRG_GOOMBA_ID_OFFSET, nes::addresses::TARGET_ENEMY_ID);

        std::cout << "[AceHarness] Writing 60-byte payload to NES RAM $03D0..." << std::endl;
        nes::MemoryAccessor::write_bytes(nes::MemoryDomain::Ram, nes::addresses::PAYLOAD_ENTRY, payload.data(), payload.size());
        nes::MemoryAccessor::write8(nes::MemoryDomain::Ram, nes::addresses::MARKER, 0x00);

        for (size_t i = 0; i < payload.size(); ++i) {
            nes::MemoryAccessor::register_cheat_override(static_cast<uint16_t>(nes::addresses::PAYLOAD_ENTRY + i), payload.bytes()[i]);
        }

        interop::Resume();
    }

    bool advance_to_gameplay() {
        int guard = 0;
        while (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::OPERMODE) != 1 && guard++ < 600) {
            DebugControllerState start_state{};
            start_state.Start = true;
            interop::SetInputOverrides(0, start_state);
            wait_frames(1);

            DebugControllerState release_state{};
            interop::SetInputOverrides(0, release_state);
            std::this_thread::sleep_for(std::chrono::milliseconds(3));
        }

        if (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::OPERMODE) != 1) {
            return false;
        }

        wait_frames(100);
        if (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::PAUSE_FLAG) & 0x01) {
            nes::MemoryAccessor::write8(nes::MemoryDomain::Ram, nes::addresses::PAUSE_FLAG, 0x00);
        }

        return true;
    }

    ExecutionResult run_verification() {
        ExecutionResult res{};

        // Send Walk Right + Jump inputs to trigger enemy spawner
        DebugControllerState walk_state{};
        walk_state.Right = true;
        walk_state.A = true;
        interop::SetInputOverrides(0, walk_state);

        int active_slot = -1;
        for (int f = 0; f < 3000; ++f) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            for (int s = 0; s < 6; ++s) {
                if (nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::ENEMY_SLOT_FLAG_BASE + s) != 0) {
                    active_slot = s;
                    break;
                }
            }
            if (active_slot >= 0) break;
        }

        DebugControllerState release_state{};
        interop::SetInputOverrides(0, release_state);

        if (active_slot < 0) {
            res.details = "No enemy object spawned within input limit";
            return res;
        }

        res.active_enemy_slot = static_cast<uint32_t>(active_slot);
        uint8_t enemy_id = nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::ENEMY_SLOT_ID_BASE + active_slot);
        std::cout << "[AceHarness] Spawned enemy in slot " << active_slot << " with ID $" << std::hex << (int)enemy_id << std::dec << std::endl;

        // Run execution for 120 frames
        wait_frames(120);

        res.marker_value = nes::MemoryAccessor::read8(nes::MemoryDomain::Ram, nes::addresses::MARKER);
        res.success = (res.marker_value == nes::addresses::TARGET_ENEMY_ID);
        res.details = res.success ? "ACE Payload executed successfully" : "Marker mismatch";

        return res;
    }

    void shutdown() {
        if (m_running) {
            interop::Stop();
            interop::Release();
            m_running = false;
        }
    }

private:
    std::filesystem::path m_rom_path;
    bool m_running{true};
};

} // namespace mesen::ace
