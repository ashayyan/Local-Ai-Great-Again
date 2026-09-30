"""E1 local one-shard FFN ternary smoke.

Streams one safetensors shard at a time. It deliberately does not load the
55.6 GB checkpoint or claim an end-to-end agreement alpha. For each FFN
matrix found in the shard, it compares an untouched linear output with a
group-128 absmean ternary fake-quantized output on one deterministic token
batch. The process stops before exceeding the 8 GiB RSS ceiling.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path

import torch
from safetensors import safe_open

RSS_LIMIT = 8 * 1024**3
FFN_MARKERS = ("mlp", "ffn", "feed_forward", "down_proj", "up_proj", "gate_proj")


def rss_bytes() -> int:
    if os.name == "nt":
        # Windows ru_maxrss is bytes in this Python build; fall back to psutil
        # when available because its units are explicit.
        try:
            import psutil
            return int(psutil.Process().memory_info().rss)
        except Exception:
            return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)


def ternary_group128(weight: torch.Tensor) -> torch.Tensor:
    flat = weight.reshape(weight.shape[0], -1)
    out = torch.empty_like(flat)
    for start in range(0, flat.shape[1], 128):
        block = flat[:, start:start + 128]
        scale = block.abs().mean(dim=1, keepdim=True).clamp_min(torch.finfo(block.dtype).eps)
        out[:, start:start + block.shape[1]] = (block / scale).round().clamp(-1, 1) * scale
    return out.reshape_as(weight)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("shard", type=Path)
    ap.add_argument("--output", type=Path, default=Path("notes/e1_layer_smoke.json"))
    ap.add_argument("--tokens", type=int, default=8)
    ap.add_argument("--hidden", type=int, default=5120)
    args = ap.parse_args()
    started = time.time()
    record = {
        "schema": "e1-layer-smoke-v1",
        "status": "pending",
        "shard": str(args.shard),
        "group_size": 128,
        "token_batch": args.tokens,
        "hidden_size": args.hidden,
        "rss_limit_bytes": RSS_LIMIT,
        "tensors": [],
        "error": None,
    }
    try:
        if not args.shard.is_file():
            raise FileNotFoundError(args.shard)
        torch.manual_seed(7)
        with safe_open(str(args.shard), framework="pt", device="cpu") as sf:
            names = [n for n in sf.keys() if any(m in n.lower() for m in FFN_MARKERS)]
            for name in names:
                if rss_bytes() >= RSS_LIMIT:
                    record["status"] = "stopped_ram_ceiling"
                    break
                w = sf.get_tensor(name)
                if w.ndim != 2 or w.numel() == 0:
                    continue
                # Keep the fixed comparison batch small and deterministic.
                x = torch.randn(args.tokens, w.shape[1], dtype=torch.float32)
                wf = w.to(torch.float32)
                baseline = x @ wf.T
                quant = ternary_group128(wf)
                approx = x @ quant.T
                mse = torch.mean((baseline - approx) ** 2).item()
                record["tensors"].append({
                    "name": name,
                    "shape": list(w.shape),
                    "mse": mse,
                    "rss_bytes": rss_bytes(),
                })
                del x, w, wf, baseline, quant, approx
            else:
                record["status"] = "measured" if record["tensors"] else "no_ffn_matrix_found"
    except Exception as exc:
        record["status"] = "error"
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["peak_rss_bytes"] = rss_bytes()
    record["elapsed_seconds"] = time.time() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0 if record["status"] in {"measured", "no_ffn_matrix_found"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
