[CmdletBinding()]
param([string]$OutputRoot='quality',[int]$Seed=0,[int]$Context=2048)
$ErrorActionPreference='Stop'
function Sha([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Rel([string]$p,[string]$root){$full=[IO.Path]::GetFullPath($p);$base=([IO.Path]::GetFullPath($root)).TrimEnd('\')+'\';if($full.StartsWith($base,[StringComparison]::OrdinalIgnoreCase)){return $full.Substring($base.Length).Replace('\','/')};return $full.Replace('\','/')}
$root=(Resolve-Path $OutputRoot).Path
$promptDir=Join-Path $root 'prompts'; $imageDir=Join-Path $root 'images'; $refDir=Join-Path $root 'reference'
New-Item -ItemType Directory -Force $promptDir,$imageDir,$refDir | Out-Null
$evalPath=Join-Path $promptDir 'text_50.json'; if(!(Test-Path $evalPath)){throw "Missing required evaluation prompts: $evalPath"}
$evalDoc=Get-Content $evalPath -Raw|ConvertFrom-Json
$eval=[object[]]$evalDoc
if($eval.Count -lt 50){throw "Expected 50 evaluation prompts; found $($eval.Count)"}
# Calibration prompts are intentionally different tasks and wording, not aliases of eval IDs.
$calPath=Join-Path $promptDir 'calibration_05.json'
$cal=@(
 [ordered]@{id='cal-001';prompt='Given bytes=1572864 and unit=MiB, compute the exact byte count and state the arithmetic.';category='numeric'},
 [ordered]@{id='cal-002';prompt='Design a two-condition benchmark table that changes only quantization while holding runtime and context fixed.';category='methodology'},
 [ordered]@{id='cal-003';prompt='Return a JSON object with keys hypothesis, observed, and next_experiment; use null for an unmeasured observed value.';category='structured'},
 [ordered]@{id='cal-004';prompt='A run reports 4 GiB VRAM and 55.6 GB of FP16 weights. Calculate the approximate decimal storage gap and name two measurement routes.';category='resource'},
 [ordered]@{id='cal-005';prompt='Explain in three ordered steps how a SHA-256 digest makes a fixture reproducible without proving model quality.';category='provenance'}
)
$cal|ConvertTo-Json -Depth 5|Set-Content $calPath -Encoding UTF8
# Small deterministic SVG fixtures: valid image files, no external assets or model claims.
$svgs=@{
 'ocr.svg'='<svg xmlns="http://www.w3.org/2000/svg" width="320" height="100"><rect width="100%" height="100%" fill="white"/><text x="20" y="60" font-family="Arial" font-size="28">OCR FIXTURE 42</text></svg>';
 'charts.svg'='<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="100%" height="100%" fill="white"/><line x1="40" y1="150" x2="290" y2="150" stroke="black"/><rect x="60" y="90" width="35" height="60" fill="#4472c4"/><rect x="120" y="55" width="35" height="95" fill="#ed7d31"/><rect x="180" y="110" width="35" height="40" fill="#70ad47"/><text x="45" y="25" font-size="18">A=3 B=5 C=2</text></svg>';
 'spatial.svg'='<svg xmlns="http://www.w3.org/2000/svg" width="240" height="160"><rect width="100%" height="100%" fill="white"/><circle cx="70" cy="80" r="25" fill="#4472c4"/><rect x="150" y="55" width="45" height="45" fill="#ed7d31"/><text x="45" y="140" font-size="16">circle left of square</text></svg>';
 'multistep.svg'='<svg xmlns="http://www.w3.org/2000/svg" width="360" height="120"><rect width="100%" height="100%" fill="white"/><text x="15" y="35" font-size="18">1 measure -&gt; 2 compare -&gt; 3 report</text><path d="M40 70 L300 70" stroke="black" marker-end="url(#a)"/></svg>'
}
foreach($n in $svgs.Keys){$p=Join-Path $imageDir $n; [IO.File]::WriteAllText($p,$svgs[$n],[Text.UTF8Encoding]::new($false))}
$images=@(); foreach($p in (Get-ChildItem $imageDir -File|Sort-Object Name)){$cat=([IO.Path]::GetFileNameWithoutExtension($p.Name));$images+=[ordered]@{category=$cat;path=(Rel $p.FullName $root);sha256=(Sha $p.FullName);bytes=[int64]$p.Length}}
$evalIds=@($eval|ForEach-Object id);$calIds=@($cal|ForEach-Object id)
$manifest=[ordered]@{schema='quality-v2';generated_utc=[DateTime]::UtcNow.ToString('o');text_prompt_count=$eval.Count;text_prompt_file='quality/prompts/text_50.json';calibration_prompt_file='quality/prompts/calibration_05.json';calibration_ids=$calIds;eval_ids=$evalIds;calibration_sha256=(Sha $calPath);eval_sha256=(Sha $evalPath);image_categories=@('OCR','charts','spatial','multistep');images=$images;image_status='fixtures-present';tokenizer_revision='unresolved';processor_revision='unresolved';model_revision='unresolved';seed=$Seed;context=$Context;scoring=[ordered]@{text='deterministic output presence, UTF-8 SHA-256, character/token counts; perplexity is null unless supplied';multimodal='fixture category coverage and output presence; no visual quality claim';unavailable='metrics use null plus status/reason'};quality_reference_status='unmeasured';immutable_fixture_rule='Hashes cover all committed fixture inputs; regenerate and compare before use'}
$manifest|ConvertTo-Json -Depth 12|Set-Content (Join-Path $root 'manifest.json') -Encoding UTF8
Write-Output "fixtures-ok prompts=$($eval.Count) calibration=$($cal.Count) images=$($images.Count)"
