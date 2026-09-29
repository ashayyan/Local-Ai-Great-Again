# 01-02 Summary — model artifact manifest and compatibility

**Scope:** E0 artifact inventory, no weights downloaded and no inference run. Implemented `scripts/s02_model_manifest.ps1` with source/revision/path arguments and offline inventory, SHA-256 per existing file, config-derived architecture fields, weight-index shard/tensor census, and explicit status/evidence for eight component classes. The generated JSON at `models/qwen3.8-27b-manifest.json` stays ignored by `.gitignore`; `notes/model_compatibility.md` compares expected versus locally observed fields and provides two metadata-only acquisition routes plus loader fallbacks. Appended an experiment to `experiments/LOG.md`.

## Verification / findings

- Command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/s02_model_manifest.ps1 -ModelPath models -Output models/qwen3.8-27b-manifest.json -Offline` — successful. JSON parses; all 8 keys exist. The plan's automated verification condition `files.Count -gt 0` does **not** pass because the available `models/` path contains zero source files. The script intentionally does not fabricate a source file or a SHA; the verification gate remains open pending metadata acquisition.
- Independent disposable fixture with config.json + tokenizer.json: command used `-ModelPath $env:TEMP\s02-manifest-fixture -Revision 0123456789abcdef0123456789abcdef01234567 -Offline`; validated two 64-character SHA-256 hashes, config `num_hidden_layers=64`, tokenizer status present. Fixture deleted after test; **not model evidence**.
- Asset findings: 0 weight files, 0 source SHA-256 hashes, 8 missing component classes, zero config-derived architecture values, source revision unresolved, no runtime pin or test. RTX 3050 VRAM measured 4096 MB and host RAM 17179869184 bytes in prior E0-HW run; model FP16/BF16 ~55.6 GB is an externally reported estimate, not locally checked.
- Bug found in nonempty-path fixture: malformed PowerShell regular expression for path separator. Corrected to literal `.Replace()`, then reran both fixture and empty-path inventory successfully. Script SHA-256 for tested working-tree version: `8a17eecf25cc6c23e7166ccc7d94a61a86b1fc384f9539374c3533411dc28117`.

## Missing artifacts and routes

Missing: immutable source commit SHA, config, tokenizer, processor, weight index, every weight shard, language/embedding/head/GDN/attention/vision/MTP tensor confirmation, and a pinned loader that actually handles each component. Route 1: fetch only config/tokenizer/processor/index at an immutable Hugging Face commit, hash each, parse architecture and index without downloading ~55.6 GB of weights. Route 2: import a revision-proven metadata-only offline cache. After metadata, test a pinned Windows-native Transformers/llama.cpp loader, then WSL2 or an architecture fixture separately if support is missing. None counts as complete multimodal inference until all tensors and runtime behaviors are checked.

## Status / Numbers / Next Experiment
- **Status:** Honest offline compatibility report produced, required-file-count verification still open for missing metadata.
- **Numbers:** 0 local source files, 0 source checksums, 8 missing classes, 0 downloaded weight bytes; 2/2 fixture files hashed in a non-model fixture.
- **Next Experiment:** Resolve immutable SHA with `python -c "from huggingface_hub import HfApi; print(HfApi().model_info('Qwen/Qwen3.8-27B').sha)"`, then run metadata-only `snapshot_download` command in `notes/model_compatibility.md` and rerun `s02_model_manifest.ps1 -Offline -Revision <40-hex-SHA>`; expected measurable result: nonzero metadata hashes, architecture fields and index shard counts, zero downloaded weight shards.
