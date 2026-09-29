# E0 PCIe small-transfer latency and cold SSD

## Pre-registration
Hypothesis: a 10 KiB hidden-state hop can be characterized with 20 pinned H2D/D2H round-trip samples, and a 17 GiB sequential file exceeds 16 GiB RAM sufficiently to measure a sustained SSD sample. Target: median/spread latency and 17 GiB read throughput.

Command: `python scripts/s14_latency_ssd.py`. Run ID: `E0-LATSSD-20260929-170531Z`.

The SSD portion completed on a temporary 17 GiB file: 18,253,611,008 bytes, write 156.46 MiB/s, sequential read 945.51 MiB/s. This is a large-file sequential sample; Windows cache state was not independently flushed, so it is not an absolute device ceiling.

The transfer portion is **invalid/unavailable** for planning: the helper used a null device address and did not assert CUDA return codes. It produced 20 timing values (median 11.50 us, range 5.80–15.90 us), but no valid H2D/D2H copy occurred. No PCIe latency number is promoted.

## Status / Numbers / Next Experiment
- **Status:** Large-file SSD sample measured; 10 KiB pinned PCIe latency invalid pending a correct device allocation and return-code checks.
- **Numbers:** 17 GiB file, 945.51 MiB/s sequential read, 156.46 MiB/s write; 20 untrusted null-address timing samples, median 11.50 us.
- **Next Experiment:** Repair the CUDA helper to allocate device memory and check every API return; measure separate pinned H2D and D2H 10 KiB medians plus round trip. Repeat SSD with documented cache policy or OS cache-bypass flags.
