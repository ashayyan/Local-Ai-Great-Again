[CmdletBinding()]
param([string]$Manifest='quality/manifest.json',[string]$OutputRoot='quality/results',[string]$OutputsPath='')
$ErrorActionPreference='Stop'
function Sha([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$m=Get-Content $Manifest -Raw|ConvertFrom-Json
New-Item -ItemType Directory -Force $OutputRoot|Out-Null
$promptPath=Join-Path (Split-Path $Manifest -Parent) 'prompts/text_50.json';$promptDoc=Get-Content $promptPath -Raw|ConvertFrom-Json;$prompts=[object[]]$promptDoc
$answers=@{}; if($OutputsPath -and (Test-Path $OutputsPath)){$doc=Get-Content $OutputsPath -Raw|ConvertFrom-Json; foreach($x in @($doc)){$answers[$x.id]=[string]$x.output}}
$rows=@(); foreach($p in $prompts){$out=if($answers.ContainsKey($p.id)){$answers[$p.id]}else{$null};$rows+=[ordered]@{id=$p.id;output_present=($null -ne $out -and $out.Trim().Length -gt 0);output_sha256=if($out){$b=[Text.Encoding]::UTF8.GetBytes($out);$sha=[Security.Cryptography.SHA256]::Create();([BitConverter]::ToString($sha.ComputeHash($b))).Replace('-','').ToLowerInvariant()}else{$null};character_count=if($out){$out.Length}else{0};perplexity=$null;status=if($out){'scored-presence-only'}else{'unavailable-no-output'}}}
$available=@($rows|Where-Object output_present).Count
$aggregate=[ordered]@{schema='quality-score-v1';generated_utc=[DateTime]::UtcNow.ToString('o');manifest_sha256=(Sha $Manifest);prompt_count=$rows.Count;outputs_available=$available;outputs_missing=$rows.Count-$available;perplexity=$null;perplexity_status='unavailable-no-logprobs';quality_claim='none';scoring_note='Deterministic presence/hash/count scoring; semantic quality requires model outputs and a separately defined reference.'}
$aggregate.prompts=$rows
$aggregate|ConvertTo-Json -Depth 10|Set-Content (Join-Path $OutputRoot 'scores.json') -Encoding UTF8
"score-ok prompts=$($rows.Count) available=$available perplexity=unavailable"
