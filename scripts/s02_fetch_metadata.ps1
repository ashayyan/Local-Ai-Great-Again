[CmdletBinding()]
param([string]$Revision='1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0',[string]$ModelPath='models',[int]$TimeoutSeconds=90)
$ErrorActionPreference='Stop'
if($Revision -notmatch '^[0-9a-f]{40}$'){throw 'Revision must be immutable 40-hex SHA'}
New-Item -ItemType Directory -Force $ModelPath | Out-Null
$names=@('config.json','generation_config.json','model.safetensors.index.json','tokenizer_config.json','preprocessor_config.json','video_preprocessor_config.json','chat_template.jinja')
foreach($name in $names){
 $url="https://huggingface.co/Qwen/Qwen3.8-27B/resolve/$Revision/$name"
 $dst=Join-Path $ModelPath $name; $tmp="$dst.partial"
 $args=@('-L','--fail','--silent','--show-error','--max-time',"$TimeoutSeconds",'--output',$tmp,$url)
 & curl.exe @args
 if($LASTEXITCODE -ne 0){Remove-Item $tmp -ErrorAction SilentlyContinue;Write-Warning "metadata unavailable: $name curl exit $LASTEXITCODE";continue}
 Move-Item -Force $tmp $dst
 $hash=(Get-FileHash $dst -Algorithm SHA256).Hash.ToLowerInvariant()
 Write-Output "$name bytes=$((Get-Item $dst).Length) sha256=$hash"
}
