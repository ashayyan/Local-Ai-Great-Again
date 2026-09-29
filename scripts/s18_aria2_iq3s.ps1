[CmdletBinding()]
param(
  [string]$Url = 'https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ3_S.gguf',
  [string]$OutputDir = 'models/ignored',
  [string]$OutputName = 'Qwen3.8-27B-UD-IQ3_S.gguf',
  [int]$MaxSeconds = 10800,
  [int]$Connections = 16
)
$ErrorActionPreference = 'Stop'
$expected = [int64]12040883104
$sha = 'd847e2c1e4aa276e4b7b8e9ad7628050e61e165d49ab995407bc36677a6f3864'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$dir = Join-Path $root $OutputDir
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$state = Join-Path $dir ($OutputName + '.aria2')
$out = Join-Path $dir $OutputName
$aria = (Get-Command aria2c -ErrorAction SilentlyContinue).Source
if (-not $aria) {
  $aria = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\aria2.aria2_Microsoft.Winget.Source_8wekyb3d8bbwe\aria2-1.37.0-win-64bit-build1\aria2c.exe'
}
if (-not (Test-Path $aria)) { throw 'aria2c not found. Install trusted winget package aria2.aria2 first.' }
$before = if (Test-Path $out) { (Get-Item $out).Length } else { [int64]0 }
$started = [DateTime]::UtcNow
$args = @('--continue=true','--allow-overwrite=false','--auto-file-renaming=false','--file-allocation=none','--check-integrity=true',('--checksum=sha-256={0}' -f $sha),'--summary-interval=30','--download-result=full',('--max-connection-per-server={0}' -f $Connections),('--split={0}' -f $Connections),'--min-split-size=4M','--max-tries=0','--retry-wait=10','--timeout=60','--connect-timeout=30',('--stop={0}' -f $MaxSeconds),('--dir={0}' -f $dir),('--out={0}' -f $OutputName),$Url)
Write-Output "Route A aria2 start utc=$($started.ToString('o')) target=$expected before_bytes=$before output=$out"
& $aria @args
$exit = $LASTEXITCODE
$after = if (Test-Path $out) { (Get-Item $out).Length } else { [int64]0 }
$elapsed = ([DateTime]::UtcNow - $started).TotalSeconds
$rate = if ($elapsed -gt 0) { (($after-$before)/1MB)/$elapsed } else { 0 }
$hash = $null
$status = 'partial'
if ($after -eq $expected) {
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $out).Hash.ToLowerInvariant()
  $status = if ($hash -eq $sha) { 'verified' } else { 'sha256_mismatch' }
}
$record = [ordered]@{schema='iq3s-acquisition-routeA-v1';route='A';url=$Url;output=$out;expected_bytes=$expected;expected_sha256=$sha;aria2_path=$aria;started_utc=$started.ToString('o');finished_utc=[DateTime]::UtcNow.ToString('o');max_seconds=$MaxSeconds;connections=$Connections;exit_code=$exit;bytes_before=$before;bytes_after=$after;bytes_added=($after-$before);rate_mib_s=[math]::Round($rate,6);status=$status;sha256=$hash;resumable_state=(Test-Path $state)}
$record | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $root 'notes/iq3s_acquisition_routeA.json')
Write-Output ($record | ConvertTo-Json -Depth 4)
if ($status -eq 'sha256_mismatch') { exit 2 }
exit 0
