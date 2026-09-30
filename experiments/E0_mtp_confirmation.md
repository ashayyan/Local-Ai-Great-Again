# E0 MTP confirmation (pre-registered)

## Hypothesis / expectation
Run the same IQ3_S configuration twice with MTP disabled and twice with `--spec-type draft-mtp`: `ngl=16`, context 2048, seed 7, `-n 128`, fixed short prompt, verbose logging. Require explicit draft/accept telemetry. Preliminary operator result was MTP 1.5 decode / 4.7 prefill versus the 1.8 / 10.3 baseline; expectation is no net speedup and possible slowdown.

## Observed run
The first baseline control artifact `experiments/raw/mtp-base-1.txt` completed generation and includes verbose timings: prompt **10.1311 t/s**, generation **1.48825 t/s**, 115 predicted tokens, and `speculative.types: none`. It has no draft/accept telemetry because it is the non-MTP control. The control process was interrupted before the remaining three runs created artifacts, so no MTP classification is made.

## Classification rules
- No accept telemetry in either MTP run: unsupported flag on this build; dormant, trigger llama.cpp MTP support for qwen35 hybrid.
- MTP engages and median is slower: dormant, trigger GPU-resident ternary draft (T1 kernel phase).
- MTP net speedup >=1.2x: record improvement but retain stock baseline as the honest bar.

## Status / Numbers / Next Experiment
- **Status:** Incomplete; one of four required verbose controls exists. No MTP result or classification is claimed.
- **Numbers:** baseline control 1.48825 decode / 10.1311 prompt t/s; seed 7; `ngl=16`; 115 predicted tokens; speculative type none.
- **Next Experiment:** rerun the remaining baseline and both MTP controls in separate bounded commands, preserving each raw file and requiring draft/accept telemetry before classification.
