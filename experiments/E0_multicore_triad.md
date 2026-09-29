# E0 multicore Triad closure probe

## Pre-registration
Hypothesis: six worker threads spanning the i5-11400H physical cores reach at least 24 GB/s-equivalent on the same 3 × 256 MiB Triad protocol. Target: 2 warmups, 7 samples, median and raw spread.

Exact command:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s13_multicore_triad.ps1 -Warmup 2 -Repetitions 7 -MiB 256 -Threads 6 -OutputJson notes/multicore_triad.json
```

Run ID: `E0-MULTICORE-20260929-165606Z`. .NET runtime 8.0.15, Windows 11 build 26200, Intel i5-11400H. Raw samples and checksum are canonical in `notes/multicore_triad.json`.

Observed median: **16,154.885 MiB/s = 16.94 GB/s decimal**, below the 24 GB/s target. This is a six-thread managed-array Triad, not a vendor STREAM ceiling; thermal/power telemetry was not captured in this run.

## Status / Numbers / Next Experiment
- **Status:** Multicore Triad measured; 24 GB/s hypothesis not met.
- **Numbers:** 6 threads, 3 × 256 MiB arrays, 2 warmups, 7 samples, median 16,154.885 MiB/s (16.94 GB/s decimal), checksum 21.
- **Next Experiment:** Run a native or optimized multithread STREAM-equivalent sweep with arrays beyond LLC and simultaneous `nvidia-smi dmon`/power-state capture; compare against this managed baseline before selecting CPU-RAM placement budgets.
