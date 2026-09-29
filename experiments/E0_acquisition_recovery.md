# E0 acquisition recovery

## Pre-registration
Hypothesis: the original direct resolve route was throttled, while HF Hub Xet, Xet-disabled HTTP, or a trusted-cache route may provide a stable resumable transfer. Target: retain partial state, measure each route in a fixed <=30 s window, and verify final 12,040,883,104 bytes plus SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864` before inference.

Artifact URL (no tokens): `https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf`.

## Route diagnostics

| Route | Window/result | Measured evidence |
|---|---|---|
| Direct curl resolve | Prior run: ~35 KB/s, ~245 MiB partial, stopped at ~94 h ETA | `scripts/s17_fetch_iq3s.ps1`; no final SHA |
| Direct HTTP bounded range | 8 MiB range completed in 1.905 s | **4.20 MiB/s**, HTTP headers report 200, content-length 12,040,883,104, `accept-ranges: bytes`; curl 8.21.0 |
| HF Hub + hf_xet | 30 s window, interrupted with resumable cache retained | Cache incomplete blob 11,061,273 bytes; no final artifact |
| HF Hub Xet disabled | 30 s window, interrupted with local cache retained | Route did not complete or produce final artifact in window; partial cache retained |
| Trusted cache/second network | Not available in this workspace | No alternate cache discovered |

The direct endpoint HEAD response identifies CloudFront (`X-Cache: Miss`, CloudFront POP `RUH50-P2`), `X-Xet-Hash: 6225746...`, and the pinned file SHA via `X-Linked-ETag`; no authentication or signed URL was recorded. HTTP client: curl 8.21.0 / libcurl Schannel. `huggingface_hub` 2.0.0 and `hf_xet` were installed for the controlled trials. `hf` executable was not exposed on PATH, so equivalent `hf_hub_download` API calls were used and recorded.

## Status / Numbers / Next Experiment
- **Status:** Exact artifact remains unacquired; both resumable HF cache states are preserved under ignored `models/hf-xet/` and `models/hf-http/`. No inference claim.
- **Numbers:** Required 12,040,883,104 bytes; SHA target `d847e2...f3864`; bounded direct HTTP range 4.20 MiB/s; previous full-route estimate ~35 KB/s; Xet partial 11,061,273 bytes; final bytes/SHA 0.
- **Next Experiment:** Resume the faster route using preserved cache with a 5-minute window, recording cumulative bytes and sustained MiB/s; if still unstable, copy the exact artifact from a trusted cache/machine and verify size/SHA locally. Keep IQ3_S revision and filename unchanged.
