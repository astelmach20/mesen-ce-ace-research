#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <thread>
#include <sys/stat.h>
#include <sys/types.h>

// Minimal driver for the MesenCore InteropDLL C API (see InteropDLL/EmuApiWrapper.cpp).
// Linked directly against the core objects; usage: fuzz_harness <rom> [frames] [homefolder]

struct TimingInfo
{
	double Fps;
	uint64_t MasterClock;
	uint32_t MasterClockRate;
	uint32_t FrameCount;
	uint32_t ScanlineCount;
	int32_t FirstScanline;
	uint32_t CycleCount;
};

extern "C"
{
	void InitDll();
	void InitializeEmu(const char* homeFolder, void* windowHandle, void* viewerHandle, bool softwareRenderer, bool noAudio, bool noVideo, bool noInput);
	bool LoadRom(char* filename, char* patchFile);
	bool IsRunning();
	void Stop();
	void Release();
	int32_t GetStopCode();
	TimingInfo GetTimingInfo(int32_t cpuType);
	void SetEmulationFlag(int32_t flag, bool enabled);
}

int main(int argc, char** argv)
{
	if(argc < 2) {
		fprintf(stderr, "usage: %s <rom> [frames] [homefolder]\n", argv[0]);
		return 2;
	}

	const char* homeFolder = argc >= 4 ? argv[3] : "/tmp/mesen_fuzz_home";
	mkdir(homeFolder, 0755);

	InitDll();
	InitializeEmu(homeFolder, nullptr, nullptr, false, true, true, true);
	SetEmulationFlag(0x04 /* MaximumSpeed */, true);
	SetEmulationFlag(0x20 /* TestMode */, true);

	if(!LoadRom(argv[1], nullptr)) {
		fprintf(stderr, "LoadRom failed\n");
		Stop();
		Release();
		return 0;
	}

	uint32_t targetFrames = argc >= 3 ? (uint32_t)strtoul(argv[2], nullptr, 10) : 3000;
	auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(600);
	while(GetTimingInfo(8).FrameCount < targetFrames) {
		if(!IsRunning()) {
			fprintf(stderr, "emulation stopped early (stop code %d)\n", GetStopCode());
			break;
		}
		if(std::chrono::steady_clock::now() > deadline) {
			fprintf(stderr, "timeout waiting for frames\n");
			break;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(10));
	}

	uint32_t frames = GetTimingInfo(8).FrameCount;
	printf("frames=%u stop=%d\n", frames, GetStopCode());

	Stop();
	Release();
	return 0;
}
