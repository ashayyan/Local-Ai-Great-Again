[CmdletBinding()]
param([string]$OutputRoot='experiments/e0_runs',[string]$RunId=('E0-'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmssZ')),[switch]$NoExecute)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$dest=Join-Path $repo $OutputRoot
New-Item -ItemType Directory -Force $dest|Out-Null
$repoSha=(& git -C $repo rev-parse HEAD 2>$null | Select-Object -First 1)
$requirements=@(
 @{name='hardware';script='s01_hardware_probe.ps1';report='notes/hardware_profile.json'},
 @{name='model_manifest';script='s02_model_manifest.ps1';report='models/qwen3.8-27b-manifest.json'},
 @{name='stock_baseline';script='s03_stock_baseline.ps1';report='experiments/raw/stock/run.json'},
 @{name='quality_fixtures';script='s04_freeze_quality.ps1';report='quality/manifest.json'},
 @{name='quality_scoring';script='s05_score_quality.ps1';report='quality/results/scores.json'},
 @{name='quant_ladder';script='s06_quant_ladder.ps1';report='quality/quant_ladder/ladder.json'}
)
$stages=@()
foreach($r in $requirements){
 $scriptPath=Join-Path $PSScriptRoot $r.script
 $reportPath=Join-Path $repo $r.report
 $stage=[ordered]@{name=$r.name;script=$r.script;script_sha256=$null;report=$r.report;report_sha256=$null;status='missing-script';command=$null;exit_code=$null}
 if(Test-Path -LiteralPath $scriptPath -PathType Leaf){
  $stage.script_sha256=(Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash.ToLowerInvariant(); $stage.status='not-run'
  if(-not $NoExecute){
   $arguments=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$scriptPath)
   if($r.name -eq 'hardware'){$arguments+=@('-RunId',$RunId,'-OutputRoot',(Join-Path $repo 'notes'),'-Samples','5','-SsdTestBytes','67108864')}
   elseif($r.name -eq 'model_manifest'){$arguments+=@('-ModelPath',(Join-Path $repo 'models'),'-Output',(Join-Path $repo $r.report),'-Offline')}
   elseif($r.name -eq 'stock_baseline'){$arguments+=@('-Context','2048','-OutputRoot',(Join-Path $repo 'experiments/raw/stock'))}
   elseif($r.name -eq 'quality_fixtures'){$arguments+=@('-OutputRoot',(Join-Path $repo 'quality'))}
   $stage.command='powershell.exe '+($arguments -join ' ')
   try{& powershell.exe @arguments | Out-Null; $stage.exit_code=$LASTEXITCODE; $stage.status=if($LASTEXITCODE -eq 0){'executed'}else{'failed'}}catch{$stage.exit_code=1;$stage.status='failed';$stage.error=$_.Exception.Message}
  }
 }
 if(Test-Path -LiteralPath $reportPath -PathType Leaf){$stage.report_sha256=(Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash.ToLowerInvariant();if($stage.status -eq 'not-run'){$stage.status='available-not-rerun'}}
 $stages+=,[pscustomobject]$stage
}
$record=[ordered]@{schema='e0-reproduction-v1';run_id=$RunId;timestamp_utc=[DateTime]::UtcNow.ToString('o');repo_commit=$repoSha;mode=if($NoExecute){'inventory'}else{'execute'};complete=$false;stages=$stages;note='A zero-exit fixture or blocked baseline is not evidence of full-model E0 completion.'}
$record|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $dest "$RunId.json") -Encoding UTF8
$record|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $dest 'latest.json') -Encoding UTF8
Write-Output "E0 run=$RunId complete=false stage_count=$($stages.Count)"
