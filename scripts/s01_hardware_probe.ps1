param([string]$RunId = "E0-HW-{0:yyyyMMdd-HHmmssZ}" -f [DateTime]::UtcNow,[string]$OutputRoot="notes",[int]$Warmups=1,[int]$Samples=5,[int64]$SsdTestBytes=67108864)
$ErrorActionPreference='Continue'; $root=(Get-Location).Path; $runDir=Join-Path $OutputRoot $RunId; New-Item -ItemType Directory -Force $runDir | Out-Null
$errors=@(); function Try-Value($name,[scriptblock]$fn){try{$v=&$fn; return @{status='measured';value=$v}}catch{$script:errors+=@{name=$name;status='error';message=$_.Exception.Message};return @{status='unavailable';value=$null}}}
$gpu=Try-Value gpu { $x=& nvidia-smi --query-gpu=name,uuid,compute_cap,memory.total,memory.free,driver_version,temperature.gpu,power.limit,clocks.gr,clocks.mem --format=csv,noheader,nounits 2>&1; if($LASTEXITCODE -ne 0){throw (($x|Out-String).Trim())}; $p=($x -split ',').ForEach({$_.Trim()}); @{name=$p[0];uuid=$p[1];compute_capability=$p[2];vram_total=$p[3];vram_free=$p[4];driver=$p[5];temperature_c=$p[6];power_limit_w=$p[7];graphics_clock_mhz=$p[8];memory_clock_mhz=$p[9]}}
$cpu=Try-Value cpu { $p=Get-CimInstance Win32_Processor | Select-Object -First 1; @{name=$p.Name;cores=$p.NumberOfCores;logical_processors=$p.NumberOfLogicalProcessors;max_clock_mhz=$p.MaxClockSpeed} }
$ram=Try-Value ram { $m=Get-CimInstance Win32_PhysicalMemory; @{total_bytes=[int64](($m|Measure-Object Capacity -Sum).Sum);modules=$m.Count} }
$os=Try-Value os { Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber }
$disk=Try-Value disk { Get-PSDrive -PSProvider FileSystem | Where Root -eq ($root.Substring(0,3)) | Select Name,Used,Free,Root }
$pcie=Try-Value pcie { $x=& nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current --format=csv,noheader,nounits 2>&1; if($LASTEXITCODE -ne 0){throw (($x|Out-String).Trim())}; $p=($x -split ',').ForEach({$_.Trim()}); @{link_generation=$p[0];link_width=$p[1]} }
$ssd=Try-Value ssd { $path=Join-Path $runDir 'ssd_probe.bin'; $sw=[Diagnostics.Stopwatch]::StartNew(); $buf=New-Object byte[] (1MB); $fs=[IO.File]::OpenWrite($path); for($i=0;$i -lt [math]::Ceiling($SsdTestBytes/1MB);$i++){$fs.Write($buf,0,$buf.Length)}; $fs.Flush();$fs.Close();$write=$sw.Elapsed.TotalSeconds; $sw.Restart();$fs=[IO.File]::OpenRead($path); while($fs.Read($buf,0,$buf.Length)-gt 0){};$fs.Close();$read=$sw.Elapsed.TotalSeconds; Remove-Item $path -Force; @{bytes=$SsdTestBytes;write_mb_s=($SsdTestBytes/1MB/$write);read_mb_s=($SsdTestBytes/1MB/$read)} }
$doc=@{schema='e0-hardware-v1';run_id=$RunId;timestamp_utc=[DateTime]::UtcNow.ToString('o');script='scripts/s01_hardware_probe.ps1';hypothesis='Windows-native probe identifies actual laptop limits with repeatable medians';numeric_target='Two runs; identity stable; repeated bandwidth/transfer samples; explicit unavailable fields';gpu=$gpu;cpu=$cpu;ram=$ram;os=$os;disk=$disk;pcie=$pcie;gpu_bandwidth=@{status='unavailable';note='CUDA copy/GEMV helper not present in this run'};cpu_bandwidth=@{status='unavailable';note='STREAM helper not present in this run'};ssd=$ssd;telemetry=@{status='measured';power_source=(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue|Select -First 1 -Expand BatteryStatus)};availability=@{nvidia_smi=($null -ne (Get-Command nvidia-smi -ErrorAction SilentlyContinue));cuda_bandwidth=$false;stream=$false};errors=$errors}
$json=$doc|ConvertTo-Json -Depth 8; $json|Set-Content (Join-Path $runDir 'hardware.json'); $json|Set-Content (Join-Path $OutputRoot 'hardware_profile.json'); $md=@"
# Hardware Profile

Run: $RunId. Raw samples: $runDir/hardware.json. Units: MB in the GPU inventory are decimal labels reported by nvidia-smi; SSD MB/s below uses MiB (1048576 bytes) and is a single cached read, **not** a sustained SSD ceiling.

| Quantity | Observed value | Status |
|---|---:|---|
| GPU | $($gpu.value.name) | $($gpu.status) |
| VRAM | $($gpu.value.vram_total) MiB reported | $($gpu.status) |
| Compute capability | $($gpu.value.compute_capability) | $($gpu.status) |
| NVIDIA driver | $($gpu.value.driver) | $($gpu.status) |
| GPU achievable bandwidth (copy) | — | unavailable: CUDA helper pending |
| FFN GEMV/GEMM achievable bandwidth | — | unavailable: CUDA helper pending |
| CPU | $($cpu.value.name), $($cpu.value.cores)C/$($cpu.value.logical_processors)T | $($cpu.status) |
| RAM capacity | $($ram.value.total_bytes) bytes | $($ram.status) |
| STREAM RAM bandwidth | — | unavailable: helper pending |
| PCIe negotiated link | Gen $($pcie.value.link_generation) x$($pcie.value.link_width) | $($pcie.status); this is not H2D throughput |
| Pinned H2D/D2H bandwidth | — | unavailable: CUDA helper pending |
| SSD sample read | $([math]::Round($ssd.value.read_mb_s,2)) MiB/s ($($ssd.value.bytes) byte cached sample) | $($ssd.status), not a sustained ceiling |
| SSD sample write | $([math]::Round($ssd.value.write_mb_s,2)) MiB/s ($($ssd.value.bytes) byte sample) | $($ssd.status), not a sustained ceiling |
| OS | $($os.value.Caption), build $($os.value.BuildNumber) | $($os.status) |

## Status / Numbers / Next Experiment
- **Status:** Partial hardware inventory; GPU, CPU, PCIe transfer, and sustained SSD bandwidth gates remain open.
- **Numbers:** $($gpu.value.vram_total) MiB VRAM, $($ram.value.total_bytes) bytes RAM, PCIe Gen $($pcie.value.link_generation) x$($pcie.value.link_width); GPU/CPU/pinned-transfer bandwidth unmeasured.
- **Next Experiment:** Implement pinned CUDA copy/FFN GEMV and CPU STREAM helpers; rerun twice with identical settings and a cold SSD file exceeding RAM cache.
"@; $md|Set-Content (Join-Path $OutputRoot 'hardware_profile.md'); "E0-HW run=$RunId JSON=$(Join-Path $runDir 'hardware.json')"