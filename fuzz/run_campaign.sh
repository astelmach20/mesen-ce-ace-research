#!/bin/bash
# Run the ASAN harness over a corpus of ROMs in parallel and collect crashes.
# Usage: run_campaign.sh <corpus_dir> [frames] [jobs]

CORPUS="${1:-corpus}"
FRAMES="${2:-240}"
JOBS="${3:-6}"
HARNESS="$(dirname "$0")/fuzz_harness_bin"
RESULTS="$(dirname "$0")/results_$(date +%H%M%S)"
mkdir -p "$RESULTS"

run_one() {
	local rom="$1"
	local base
	base="$(basename "$rom")"
	local out="$RESULTS/$base.log"
	ASAN_OPTIONS=abort_on_error=1:detect_leaks=0 "$HARNESS" "$rom" "$FRAMES" >"$out" 2>&1
	local rc=$?
	if [ $rc -ne 0 ]; then
		echo "CRASH rc=$rc rom=$rom"
		cp "$rom" "$RESULTS/$base.nes"
	fi
}
export -f run_one
export HARNESS RESULTS FRAMES

find "$CORPUS" -name '*.nes' -print0 | xargs -0 -P "$JOBS" -I{} bash -c 'run_one "$1"' _ {} > "$RESULTS/summary.txt" 2>&1

echo "done; crashes:"
rg -c "CRASH" "$RESULTS/summary.txt" || true
