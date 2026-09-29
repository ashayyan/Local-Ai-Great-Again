# E0 CPU STREAM-like benchmark

## Hypothesis and target (before run)
A Release .NET array Triad over three 256 MiB arrays, after 2 warmups, should reach a median of at least **10,000 MiB/s** for seven measured repetitions on this Windows host. The benchmark reports raw samples, median, and a checksum to detect dead-code elimination.

## Reproduction
From the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s09_cpu_stream.ps1 -Warmup 2 -Repetitions 7 -MiB 256 -OutputJson notes/cpu_stream.json
```

`pwsh` is not installed on this host; `powershell.exe` (Windows PowerShell 5.1.26100.9168) was used. The script invokes `dotnet run --project scripts/cpu_stream/CpuStream.csproj --configuration Release` and uses the available .NET 9.0.203 SDK. The project targets `net8.0`, executing on .NET runtime 8.0.15.

## Actual run
- Repository commit before run: `6c47565c4c26000da949d9c3d09e2ac2b086d44b` (branch `master`)
- OS: Windows 10.0.26200 (x64)
- .NET SDK: 9.0.203 (SDK commit `dc7acfa194`); runtime: 8.0.15
- CPU identifier: `Intel64 Family 6 Model 141 Stepping 1, GenuineIntel`
- Arrays: 3 × 256 MiB `double`; Triad operation `C[i] = A[i] + 3*B[i]`; checksum `21`
- Warmup/repetitions: 2 / 7
- Raw MiB/s: 9660.425964, 11516.919224, 11826.374046, 11978.009124, 12345.619475, 12473.809872, 12485.409304
- Median: **11978.009123874139 MiB/s**

The target was exceeded (11978.01 / 10000 = 1.20×). `notes/cpu_stream.json` contains the machine-readable summary and raw samples. This is a single-thread managed-array, warm-cache STREAM-like Triad; it does **not** establish the maximum achievable multicore DRAM bandwidth. No CUDA or `nvcc` is required.

## Status / Numbers / Next Experiment
- **Status:** One Windows-native Triad benchmark completed; multicore RAM bandwidth ceiling remains open.
- **Numbers:** 11,978.009 MiB/s median (12.56 GB/s decimal), 7 measured repetitions, 2 warmups, 3 × 256 MiB arrays.
- **Next Experiment:** Run a pinned multithread STREAM-equivalent sweep over array sizes larger than last-level cache under the same power profile; compare medians and thermal state.
