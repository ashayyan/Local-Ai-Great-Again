[CmdletBinding()]
param([int]$Warmup=2,[int]$Repetitions=7,[int]$MiB=256,[string]$OutputJson='notes/multicore_triad.json',[int]$Threads=6)
$ErrorActionPreference='Stop'; $project=Join-Path $PSScriptRoot 'cpu_stream/CpuStream.csproj'
if(-not (Get-Command dotnet -ErrorAction SilentlyContinue)){throw 'dotnet CLI unavailable'}
$runId='E0-MULTICORE-'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmssZ')
$raw=& dotnet run --project $project --configuration Release -- --warmup $Warmup --repetitions $Repetitions --mib $MiB --threads $Threads 2>&1
if($LASTEXITCODE -ne 0){throw ($raw -join [Environment]::NewLine)}
$summary=($raw|Where-Object {$_ -match '^?\{"type":"summary"'}|Select-Object -Last 1)
if(-not $summary){throw 'No summary JSON'}
$j=$summary|ConvertFrom-Json; $j|Add-Member NoteProperty run_id $runId; $j|Add-Member NoteProperty threads $Threads; $j|Add-Member NoteProperty hypothesis 'All physical cores Triad reaches at least 24 GB/s'; $j|Add-Member NoteProperty numeric_target '2 warmups, 7 samples, median >=24 GB/s'; $j|ConvertTo-Json -Depth 8|Set-Content $OutputJson -Encoding UTF8
$j|ConvertTo-Json -Depth 8
