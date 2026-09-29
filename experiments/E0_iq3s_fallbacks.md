# E0 IQ3_S fallback acquisition routes

**Hypothesis / target.** The same Unsloth `Qwen3.8-27B-UD-IQ3_S.gguf` (12,040,883,104 bytes; SHA-256 `d847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864`) is available through both Hugging Face and ModelScope. A bounded first-1-MiB request (30-second cap) should establish route reachability and relative speed without committing to a 12-GB download. No model change was made.

## Metadata/API

- Hugging Face API returned HTTP 200; repo commit `4ca720788d1e01f1bff70c033e0d0028fd02e502`; file listed with expected size and SHA; repository is not gated. Source: https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF
- ModelScope API returned HTTP 200; `unsloth/Qwen3.8-27B-GGUF` lists the same IQ3_S artifact, size and SHA. Source: https://modelscope.cn/api/v1/models/unsloth/Qwen3.8-27B-GGUF

## Bounded route tests

Commands used (secrets omitted from notes):

```powershell
curl.exe -L --fail --max-time 30 --range 0-1048575 -o models/iq3s-route-http.partial "https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf?download=true"
curl.exe -L --fail --max-time 30 --range 0-1048575 -o models/iq3s-route-modelscope.partial "https://modelscope.cn/models/unsloth/Qwen3.8-27B-GGUF/resolve/master/Qwen3.8-27B-UD-IQ3_S.gguf"
```

| Route | HTTP/status | Bytes | Elapsed | Measured rate | Result |
|---|---:|---:|---:|---:|---|
| Hugging Face HTTP/Xet | 200 / range_ok | 1,048,576 | 1.490 s | 703,700 B/s (0.67 MiB/s) | reachable; preferred |
| ModelScope | 200 / range_ok | 1,048,576 | 3.446 s | 304,322 B/s (0.29 MiB/s) | reachable; fallback |

The partial files remain under ignored `models/` and are intentionally not deleted. At measured rates, a naive 12,040,883,104-byte transfer would be approximately 4.8 h (HF) or 11.0 h (ModelScope); actual rates can vary and resumable transfer is required.

## hf_transfer availability

Python 3.13.2 is present, but `hf_transfer` is absent. PyPI reports latest release 0.1.9 (https://pypi.org/pypi/hf_transfer/json). It was **not installed**: route confirmation succeeded with plain HTTP, and the request explicitly prohibited enabling a high-performance HF flag. `HF_HUB_ENABLE_HF_TRANSFER` was not set. Installing it later would require a bounded comparison under the current Python/platform, but it is not needed to establish availability or fallback reachability.

## Status / Numbers / Next Experiment

- **Status:** Both acquisition routes verified by metadata and bounded transfer; full 12-GB download not attempted; no model change; no tokens/signed URLs recorded.
- **Numbers:** 12,040,883,104 bytes; SHA-256 `d847e2c1…3864`; HF 0.67 MiB/s vs ModelScope 0.29 MiB/s in 1-MiB probes (2.31x HF advantage); `hf_transfer` absent, latest PyPI 0.1.9.
- **Next Experiment:** Resume a real download using Hugging Face first, preserve partial cache, and verify final SHA-256; switch to ModelScope only if HF stalls or errors.
