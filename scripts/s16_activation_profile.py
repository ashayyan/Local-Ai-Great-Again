"""E3.1 activation sparsity profiler (offline-first, no weight downloads).

The harness profiles native SiLU/SwiGLU modules exposed by a Transformers model.
It never downloads a model: --local-files-only is always set. Missing assets,
dependencies, or a runtime are emitted as structured ``unavailable`` results.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path

SCHEMA = "e3.1-activation-profile-v1"
DEFAULT_CATEGORIES = {
    "instruction": "Explain a technical concept clearly, with assumptions, steps, and a concise example.",
    "code": "Write and review a small Python function, identify edge cases, and explain its complexity.",
    "reasoning": "Solve a multi-step planning problem, compare alternatives, and check the conclusion.",
    "factual": "Describe relevant facts about science, history, geography, and everyday systems accurately.",
}


def blocker(kind: str, message: str) -> dict:
    return {"kind": kind, "message": message}


def local_model_path(value: str | None) -> str | None:
    if value:
        return value
    root = Path("models")
    if not root.exists():
        return None
    candidates = [p for p in root.iterdir() if p.is_dir() and (p / "config.json").exists()]
    return str(sorted(candidates)[0]) if candidates else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", help="local Transformers model directory (never downloaded)")
    p.add_argument("--tokenizer", help="local tokenizer directory (defaults to --model)")
    p.add_argument("--output", default="notes/activation_profile.json")
    p.add_argument("--min-tokens", type=int, default=1000)
    p.add_argument("--max-seq-len", type=int, default=512)
    p.add_argument("--top-k", type=float, nargs="+", default=[0.01, 0.10])
    p.add_argument("--inactive-threshold", type=float, default=1e-3)
    p.add_argument("--sample-values", type=int, default=200000)
    args = p.parse_args()
    model_path = local_model_path(args.model)
    tokenizer_path = args.tokenizer or model_path
    doc = {
        "schema": SCHEMA, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script": "scripts/s16_activation_profile.py", "status": "unavailable",
        "hypothesis": "Native SiLU/SwiGLU activations have category-dependent magnitude tails and inactive fractions that can guide E3.1 sparsity routes.",
        "target": {"minimum_tokens": args.min_tokens, "categories": list(DEFAULT_CATEGORIES),
                   "metrics": ["count", "mean_abs", "p50_abs", "p90_abs", "p99_abs", "max_abs", "top_k_abs_mass", "inactive_fraction"]},
        "pre_registration": {"command": "python scripts/s16_activation_profile.py --model <LOCAL_MODEL> --tokenizer <LOCAL_TOKENIZER> --output notes/activation_profile.json",
                              "routes": ["free local Transformers/PyTorch run with --model/--tokenizer", "borrowed compute rerun with the same command and artifact schema", "if native hooks are unsupported, add an architecture-specific hook adapter without changing thresholds"],
                              "status": "pre-registered"},
        "model": model_path, "tokenizer": tokenizer_path, "runtime": {"python": sys.version.split()[0], "os": platform.platform()},
        "tokens": {"required": args.min_tokens, "observed": 0}, "categories": {}, "layers": {}, "blockers": [],
    }
    if args.min_tokens < 1000:
        doc["blockers"].append(blocker("configuration", "--min-tokens must be >= 1000 (activation profile requires at least 1000 tokens)"))
    if not model_path:
        doc["blockers"].append(blocker("model", "local model absent: no --model supplied and models/ contains no directory with config.json"))
    elif not Path(model_path).exists():
        doc["blockers"].append(blocker("model", f"local model absent: --model path does not exist: {model_path}"))
    if not tokenizer_path:
        doc["blockers"].append(blocker("tokenizer", "local tokenizer absent: supply --tokenizer or a model directory containing tokenizer files"))
    elif not Path(tokenizer_path).exists():
        doc["blockers"].append(blocker("tokenizer", f"local tokenizer absent: --tokenizer path does not exist: {tokenizer_path}"))
    if doc["blockers"]:
        return finish(doc, args.output)
    try:
        import torch
        import transformers
        doc["runtime"].update({"torch": torch.__version__, "transformers": transformers.__version__, "device": "cuda" if torch.cuda.is_available() else "cpu"})
    except Exception as exc:
        doc["blockers"].append(blocker("dependency", f"PyTorch/Transformers dependency unavailable: {type(exc).__name__}: {exc}"))
        return finish(doc, args.output)
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype="auto")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device).eval()
        doc["runtime"]["device"] = device
    except Exception as exc:
        doc["blockers"].append(blocker("model/runtime", f"local model load/runtime blocker: {type(exc).__name__}: {exc}"))
        doc["traceback"] = traceback.format_exc()
        return finish(doc, args.output)

    # Build category prompts and repeat each enough times to guarantee a >=1000-token corpus.
    encoded = {}
    total = 0
    for category, text in DEFAULT_CATEGORIES.items():
        ids = tokenizer(text, add_special_tokens=True, return_tensors="pt")["input_ids"][0]
        repeats = max(1, math.ceil(args.min_tokens / max(1, len(ids) * len(DEFAULT_CATEGORIES))))
        ids = ids.repeat(repeats)
        encoded[category] = ids
        total += len(ids)
    while total < args.min_tokens:
        category = list(encoded)[total % len(encoded)]
        encoded[category] = torch.cat([encoded[category], encoded[category][: min(len(encoded[category]), args.min_tokens - total)]])
        total = sum(len(x) for x in encoded.values())
    doc["tokens"]["observed"] = total
    doc["categories"] = {k: int(len(v)) for k, v in encoded.items()}
    buckets = defaultdict(list)
    handles = []

    def hook(kind, name):
        def capture(_module, _inputs, output):
            value = output[0] if isinstance(output, (tuple, list)) else output
            if not hasattr(value, "detach"):
                return
            flat = value.detach().float().abs().reshape(-1).cpu().tolist()
            b = buckets[(current_category, kind, name)]
            remaining = max(0, args.sample_values - len(b))
            if remaining:
                b.extend(flat[:remaining])
        return capture

    for name, module in model.named_modules():
        cname = module.__class__.__name__.lower()
        if cname == "silu" or "swiglu" in cname:
            kind = "silu" if cname == "silu" else "swiglu"
            handles.append(module.register_forward_hook(hook(kind, name)))
    doc["hooked_modules"] = len(handles)
    if not handles:
        doc["blockers"].append(blocker("architecture", "no native nn.SiLU or SwiGLU modules exposed by model; architecture-specific hook adapter required"))
        return finish(doc, args.output)
    current_category = ""
    try:
        with torch.no_grad():
            for current_category, ids in encoded.items():
                for start in range(0, len(ids), args.max_seq_len):
                    chunk = ids[start:start + args.max_seq_len].unsqueeze(0).to(device)
                    model(input_ids=chunk, attention_mask=torch.ones_like(chunk))
    except Exception as exc:
        doc["blockers"].append(blocker("runtime", f"activation forward pass blocker: {type(exc).__name__}: {exc}"))
        doc["traceback"] = traceback.format_exc()
    finally:
        for handle in handles:
            handle.remove()
    for (category, kind, name), values in buckets.items():
        if not values:
            continue
        values.sort()
        n = len(values)
        total_abs = sum(values)
        result = {"kind": kind, "samples": n, "mean_abs": total_abs / n,
                  "p50_abs": values[min(n - 1, int(.50 * n))], "p90_abs": values[min(n - 1, int(.90 * n))],
                  "p99_abs": values[min(n - 1, int(.99 * n))], "max_abs": values[-1],
                  "inactive_fraction": sum(v <= args.inactive_threshold for v in values) / n}
        result["top_k_abs_mass"] = {str(k): (sum(values[max(0, n - max(1, int(n * k))):]) / total_abs if total_abs else 0.0) for k in args.top_k}
        doc["layers"].setdefault(name, {}).setdefault(category, {})[kind] = result
    if doc["tokens"]["observed"] < 1000:
        doc["blockers"].append(blocker("token-count", f"only {doc['tokens']['observed']} tokens profiled; required >= 1000"))
    doc["status"] = "measured" if not doc["blockers"] else "unavailable"
    return finish(doc, args.output)


def finish(doc: dict, output: str) -> int:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0 if doc["status"] == "measured" else 2


if __name__ == "__main__":
    raise SystemExit(main())
