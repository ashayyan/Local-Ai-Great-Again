[CmdletBinding()]
param(
  [int]$Warmup = 2,
  [int]$Repetitions = 7,
  [int]$MiB = 256,
  [string]$OutputJson
)
$ErrorActionPreference = 'Stop'
if ($Warmup -lt 0 -or $Repetitions -lt 1 -or $MiB -lt 1) { throw 'Warmup >= 0, Repetitions >= 1, MiB >= 1 required.' }
$root = Split-Path -Parent $PSScriptRoot
$project = Join-Path $PSScriptRoot 'cpu_stream/CpuStream.csproj'
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) { throw 'dotnet CLI not found.' }
$run = & dotnet run --project $project --configuration Release -- --warmup $Warmup --repetitions $Repetitions --mib $MiB 2>&1
if ($LASTEXITCODE -ne 0) { throw "dotnet run failed ($LASTEXITCODE): $($run -join [Environment]::NewLine)" }
$run | ForEach-Object { Write-Output $_ }
$summaryLine = $run | Where-Object { $_ -match '^\{"type":"summary"' } | Select-Object -Last 1
if (-not $summaryLine) { throw 'Benchmark produced no summary JSON.' }
if ($OutputJson) {
  $summaryLine | Set-Content -LiteralPath $OutputJson -Encoding utf8
  Write-Output "Wrote summary: $OutputJson"
}
