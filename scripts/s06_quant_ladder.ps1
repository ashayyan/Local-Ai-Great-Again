[CmdletBinding()]
param([string]$ModelRoot='models',[string]$OutputRoot='quality/quant_ladder',[int]$Context=2048,[int]$Seed=0)
$ErrorActionPreference='Stop';New-Item -ItemType Directory -Force $OutputRoot|Out-Null
$manifest=Join-Path $OutputRoot 'ladder.json';$tiers=@(
 [ordered]@{tier='Q4/NVFP4';patterns=@('*q4*','*nvfp4*')},
 [ordered]@{tier='Q3/IQ3';patterns=@('*q3*','*iq3*')},
 [ordered]@{tier='Q2/IQ2';patterns=@('*q2*','*iq2*')}
)
$records=@();foreach($t in $tiers){$files=@();foreach($pat in $t.patterns){$files+=@(Get-ChildItem $ModelRoot -Recurse -File -Filter $pat -ErrorAction SilentlyContinue)};$files=@($files|Sort-Object FullName -Unique);$status=if($files.Count){'available-not-run-no-runtime'}else{'unavailable-no-matching-weights'};$records+=[ordered]@{tier=$t.tier;status=$status;artifacts=@($files|ForEach-Object{[ordered]@{path=$_.FullName;bytes=[int64]$_.Length;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}});context=$Context;seed=$Seed;load_time_seconds=$null;ttft_seconds=$null;prefill_tok_s=$null;decode_tok_s=$null;vram_peak_bytes=$null;ram_peak_bytes=$null;quality_score=$null;quality_status='unavailable-not-executed';reason=if($files.Count){'Runtime invocation intentionally not configured; artifact presence is not a measurement.'}else{'No local matching weight artifact.'}}}
$out=[ordered]@{schema='quant-ladder-v1';generated_utc=[DateTime]::UtcNow.ToString('o');hypothesis='Matched context/seed/settings permit one-variable quant comparison when runtime and weights exist.';fixed_settings=[ordered]@{context=$Context;seed=$Seed;model_root=$ModelRoot};tiers=$records;claim='No quality claim; unavailable values remain null.'}
$out|ConvertTo-Json -Depth 12|Set-Content $manifest -Encoding UTF8
"ladder-ok tiers=$($records.Count) unavailable=$(@($records|Where-Object status -like 'unavailable*').Count)"
