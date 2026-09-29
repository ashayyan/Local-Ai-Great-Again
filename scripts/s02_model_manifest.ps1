[CmdletBinding()]
param(
    [string]$ModelPath = 'models',
    [string]$Output = 'models/qwen3.8-27b-manifest.json',
    [string]$Source = 'Qwen/Qwen3.8-27B',
    [string]$Revision = '',
    [string]$TokenizerRevision = '',
    [string]$ProcessorRevision = '',
    [switch]$Offline
)
$ErrorActionPreference = 'Stop'
# Inventory only: no network, model loads, or weight allocations, even without -Offline.
function Full-Path([string]$p) { return [IO.Path]::GetFullPath($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p)) }
function Has-File([string]$name) { return ($script:fileNames -contains $name) }
function Component([string]$status, [string]$evidence) { return [ordered]@{ status = $status; evidence = $evidence } }
function Field($obj, [string]$name) {
    if ($null -ne $obj -and $obj.PSObject.Properties.Name -contains $name) { return $obj.$name }
    return $null
}
$modelRoot = Full-Path $ModelPath
$outputPath = Full-Path $Output
if (!(Test-Path -LiteralPath $modelRoot -PathType Container)) { throw "ModelPath must be an existing directory: $modelRoot" }
$items = @(Get-ChildItem -LiteralPath $modelRoot -Recurse -File | Where-Object { $_.FullName -ne $outputPath } | Sort-Object FullName)
$files = @()
foreach ($item in $items) {
    $relative = $item.FullName.Substring($modelRoot.Length).TrimStart('\','/').Replace('\','/')
    $name = $item.Name.ToLowerInvariant()
    $kind = if ($name -match '\.gguf$') { 'GGUF' } elseif ($name -match '\.safetensors$') { 'safetensors' } elseif ($name -match 'nvfp4') { 'NVFP4-metadata' } elseif ($name -match 'tokenizer|vocab|merges|sentencepiece|\.model$') { 'tokenizer' } elseif ($name -match 'processor|preprocessor|image') { 'processor' } elseif ($name -eq 'config.json') { 'config' } elseif ($name -match 'index\.json$') { 'weight-index' } else { 'other/reference' }
    $files += [ordered]@{path=$relative; bytes=[int64]$item.Length; sha256=(Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant(); status='present'; kind=$kind}
}
$script:fileNames = @($files | ForEach-Object { $_.path })
$configPath = Join-Path $modelRoot 'config.json'
$config = $null
$configError = $null
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    try { $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -ErrorAction Stop }
    catch { $configError = $_.Exception.Message }
}
$text = if ($null -ne (Field $config 'text_config')) { Field $config 'text_config' } else { $config }
$vision = Field $config 'vision_config'
$layerTypes = @(Field $text 'layer_types' | Where-Object { $null -ne $_ })
$fullCount = @($layerTypes | Where-Object { "$_" -match 'full_attention' }).Count
$gdnCount = @($layerTypes | Where-Object { "$_" -match 'linear_attention|gated_delta|gdn' }).Count
$architecture = [ordered]@{
    model_type = Field $config 'model_type'; text_model_type = Field $text 'model_type'
    num_hidden_layers = Field $text 'num_hidden_layers'; hidden_size = Field $text 'hidden_size'
    intermediate_size = Field $text 'intermediate_size'; vocab_size = Field $text 'vocab_size'
    num_attention_heads = Field $text 'num_attention_heads'; num_key_value_heads = Field $text 'num_key_value_heads'
    tie_word_embeddings = Field $config 'tie_word_embeddings'
    layer_types = $layerTypes; gdn_layer_count = if ($layerTypes.Count) { $gdnCount } else { $null }
    full_attention_layer_count = if ($layerTypes.Count) { $fullCount } else { $null }
    vision_num_hidden_layers = if ($null -ne (Field $vision 'depth')) { Field $vision 'depth' } else { Field $vision 'num_hidden_layers' }
    num_nextn_predict_layers = if ($null -ne (Field $text 'mtp_num_hidden_layers')) { Field $text 'mtp_num_hidden_layers' } else { Field $text 'num_nextn_predict_layers' }
}
# A named file is evidence of an artifact, not evidence of correct tensors or runtime support.
$weights = @($files | Where-Object { $_.kind -in @('safetensors','GGUF') })
$weightIndex = @($files | Where-Object { $_.path -match '(^|/)(model\.safetensors\.index\.json|pytorch_model\.bin\.index\.json)$' })
$indexKeys = @()
$indexError = $null
if ($weightIndex.Count -eq 1) {
    try {
        $indexDoc = Get-Content -LiteralPath (Join-Path $modelRoot ($weightIndex[0].path.Replace('/', [IO.Path]::DirectorySeparatorChar))) -Raw | ConvertFrom-Json -ErrorAction Stop
        $indexKeys = @($indexDoc.weight_map.PSObject.Properties.Name)
    } catch { $indexError = $_.Exception.Message }
}
$tokenizerFiles = @($files | Where-Object { $_.path -match '(^|/)(tokenizer\.json|tokenizer\.model|vocab\.json)$' })
$processorFiles = @($files | Where-Object { $_.path -match '(^|/)(preprocessor_config\.json|processor_config\.json|image_processor_config\.json)$' })
$indexShards = @()
$missingShards = @()
if ($indexKeys.Count) {
    $indexShards = @($indexDoc.weight_map.PSObject.Properties.Value | Sort-Object -Unique)
    $missingShards = @($indexShards | Where-Object { $script:fileNames -notcontains ("$_" -replace '\\','/') })
}
$components = [ordered]@{}
$components.language = if ($weights.Count) { Component 'unsupported' 'Weight files exist; shard inventory does not prove complete tensor coverage or stock loader execution.' } else { Component 'missing' 'No safetensors or GGUF weight file found.' }
$components.embeddings = if ($weights.Count) { Component 'unsupported' 'Input embedding and untied lm_head tensor names/shapes have not been verified against a weight index.' } else { Component 'missing' 'No weight artifacts for input embedding and output lm_head.' }
$components.GDN = if ($weights.Count) { Component 'unsupported' 'Weight files found, but GDN tensor coverage and runtime execution unverified.' } else { Component 'missing' 'No weight artifact for GDN blocks.' }
$components.attention = if ($weights.Count) { Component 'unsupported' 'Weight files found, but full-attention tensor coverage and runtime execution unverified.' } else { Component 'missing' 'No weight artifact for full-attention blocks.' }
$components.vision = if ($weights.Count) { Component 'unsupported' 'Weight files found, but vision tower and projector tensor coverage unverified.' } else { Component 'missing' 'No weight artifact for vision tower/projector.' }
$components.tokenizer = if ($tokenizerFiles.Count) { Component 'present' ('Tokenizer file(s): ' + (($tokenizerFiles | ForEach-Object path) -join ', ') + '; behavior untested.') } else { Component 'missing' 'No tokenizer.json/tokenizer.model/vocab.json.' }
$components.processor = if ($processorFiles.Count) { Component 'present' ('Processor metadata file(s): ' + (($processorFiles | ForEach-Object path) -join ', ') + '; image behavior untested.') } else { Component 'missing' 'No preprocessor_config.json/processor_config.json/image_processor_config.json.' }
$components.MTP = if ($weights.Count) { Component 'unsupported' 'Native MTP weight and loader support unverified.' } else { Component 'missing' 'No weight artifact for native MTP layer.' }
$revisionStatus = if ($Revision -match '^[0-9a-fA-F]{40}$') { 'pinned-sha-input-unverified' } elseif ($Revision) { 'unverified-non-sha-input' } else { 'unresolved-offline' }
$sourceRevision = if ($Revision) { $Revision } else { 'UNRESOLVED: no local immutable source revision' }
$metadata = [ordered]@{
    schema = 'e0-model-manifest-v1'; generated_utc = [DateTime]::UtcNow.ToString('o'); offline = [bool]$Offline
    source = $Source; source_revision = $sourceRevision; source_revision_status = $revisionStatus
    tokenizer_revision = if ($TokenizerRevision) { $TokenizerRevision } else { 'unresolved' }
    processor_revision = if ($ProcessorRevision) { $ProcessorRevision } else { 'unresolved' }
    model_path = $modelRoot; config_status = if ($configError) { 'invalid' } elseif ($config) { 'present' } else { 'missing' }
    config_error = $configError; architecture = $architecture; files = @($files)
    missing_expected_files = if ($files.Count) { @() } else { @('config.json','model.safetensors.index.json','model-*.safetensors','tokenizer.json','preprocessor_config.json') }
    weight_index_count = $weightIndex.Count; weight_index_error = $indexError
    weight_index_tensor_count = $indexKeys.Count; weight_index_shards = $indexShards
    missing_index_shards = $missingShards; components = $components
    compatibility = [ordered]@{ status = 'unverified'; reason = 'No model execution or pinned loader test performed by this inventory script.' }
}
$parent = Split-Path -Parent $outputPath
if (!(Test-Path -LiteralPath $parent -PathType Container)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$metadata | ConvertTo-Json -Depth 24 | Set-Content -LiteralPath $outputPath -Encoding UTF8
Write-Output "Manifest: $outputPath; present files=$($files.Count); source revision=$revisionStatus; compatibility=unverified"
