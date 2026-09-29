# E0 architecture amendment and resequencing

## New measured consequence
The six-thread Triad probe measured **16.94 GB/s decimal median** against the pre-registered >=24 GB/s target. A CPU-side 2.67 GB ternary FFN therefore estimates approximately 4.5–5.3 tok/s before MTP under η=0.7–0.85. This places the original T3 route at the 5 tok/s project target without margin.

## Amendment
T3 merges with T4 for placement design:

- Keep GDN/attention/lm_head and hot ternary FFN rows in approximately 1.3 GB spare VRAM after the planned 2.5-bit hot state.
- Stream only cold FFN rows from RAM.
- If native activation sparsity is measured, expected RAM bytes/token may fall approximately 2×, giving a provisional 8–10 tok/s ceiling. This is a hypothesis, not a result.
- Promotion gate: E3.1 native activation profile over >=1,000 tokens.

## Resequencing decision
E3.1 is advanced to run in parallel with E2 because it determines whether hot-row/cold-row placement can reduce RAM traffic, while it is independent of E1 agreement alpha and can use free/borrowed compute if the local runtime cannot execute the full model. E2 still owns sm_86 kernels and transfer accounting; E3.1 owns native activation evidence and sparsity statistics.

## Status / Numbers / Next Experiment
- **Status:** T3/T4 amendment and E3.1 parallel resequencing recorded; no sparse-placement promotion.
- **Numbers:** Triad 16.94 GB/s; original target 24 GB/s; estimated CPU ternary route 4.5–5.3 tok/s at η=0.7–0.85; provisional sparsity hypothesis 2× RAM-byte reduction and 8–10 tok/s ceiling.
- **Next Experiment:** Run E3.1 native hooks on >=1,000 tokens using free/borrowed compute fallback while E2 builds sm_86 kernels and measures placement.
