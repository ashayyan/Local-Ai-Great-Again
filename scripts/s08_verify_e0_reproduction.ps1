[CmdletBinding()]
param([string]$RepoRoot='.',[string]$OutputRoot='experiments/e0_runs')
$ErrorActionPreference='Stop'
$repo=(Resolve-Path $RepoRoot).Path
$root=Join-Path $repo $OutputRoot
New-Item -ItemType Directory -Force $root|Out-Null
$required=@('s01_hardware_probe.ps1','s02_model_manifest.ps1','s03_stock_baseline.ps1','s04_freeze_quality.ps1','s05_score_quality.ps1','s06_quant_ladder.ps1','s07_run_e0.ps1','s08_verify_e0_reproduction.ps1')
$missing=@($required|Where-Object {-not (Test-Path -LiteralPath (Join-Path $repo "scripts/$_") -PathType Leaf)})
$manifest=Join-Path $root 'latest.json'; $stages=@(); if(Test-Path $manifest){$j=Get-Content $manifest -Raw|ConvertFrom-Json;$stages=@($j.stages)}
$errors=@(); if($missing.Count){$errors+=('Missing scripts: '+($missing -join ', '))}
if($stages.Count -ne 6){$errors+="Expected six E0 stages; found $($stages.Count)"}
$source=(Get-ChildItem (Join-Path $repo 'scripts') -Filter 's*.ps1' -File | Sort-Object Name | ForEach-Object {@{name=$_.Name;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
$record=[ordered]@{schema='e0-clean-checkout-v1';timestamp_utc=[DateTime]::UtcNow.ToString('o');status='partial';structure_valid=($errors.Count -eq 0);complete=$false;model_reproduced=$false;stage_count=$stages.Count;missing_scripts=$missing;errors=$errors;script_hashes=@($source);note='Structural verification only; no actual fresh clone, model rerun, or E0 gate pass.'}
$record|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $root 'clean-checkout.json') -Encoding UTF8
Write-Output "structural_status=$($record.status) model_reproduced=false missing_scripts=$($missing.Count)"
if($errors.Count){exit 2}
