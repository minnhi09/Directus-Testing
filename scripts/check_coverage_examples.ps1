# Static parsing only: never invoke the lab wrappers or load lab.env.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$coverageRoot = Join-Path $repoRoot 'docs/coverage'

$psFiles = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1' -File)
$windowsScripts = Join-Path $PSScriptRoot 'windows'
if (Test-Path -LiteralPath $windowsScripts) {
    $psFiles += @(Get-ChildItem -LiteralPath $windowsScripts -Filter '*.ps1' -File)
}
foreach ($file in $psFiles) {
    $tokens = $null
    $parseErrors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile(
        $file.FullName, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) {
        throw "PowerShell syntax failed: $($file.Name)"
    }
}

if (-not (Get-Command Test-Json -ErrorAction SilentlyContinue)) {
    throw 'Missing Test-Json; do not install or upgrade automatically.'
}
$common = Get-Content -LiteralPath (Join-Path $coverageRoot 'schemas/common.schema.json') -Raw |
    ConvertFrom-Json -AsHashtable

# Resolve only the local common definitions used by the P01 contract.
# No URI is fetched; unexpected reference targets fail closed.
function Expand-LocalSchema($node) {
    if ($node -is [System.Collections.IDictionary]) {
        if ($node.Contains('$ref')) {
            $prefix = 'common.schema.json#/$defs/'
            if (-not $node['$ref'].StartsWith($prefix)) {
                throw 'Unexpected schema reference; only local common definitions are supported.'
            }
            $name = $node['$ref'].Substring($prefix.Length)
            if (-not $common['$defs'].Contains($name)) {
                throw "Unknown common definition: $name"
            }
            return Expand-LocalSchema $common['$defs'][$name]
        }
        $copy = [ordered]@{}
        foreach ($key in $node.Keys) {
            $copy[$key] = Expand-LocalSchema $node[$key]
        }
        return $copy
    }
    if ($node -is [System.Collections.IList]) {
        $items = @(foreach ($item in $node) { Expand-LocalSchema $item })
        return ,$items
    }
    return $node
}

$recordCount = 0
$exampleFiles = @(Get-ChildItem -LiteralPath (Join-Path $coverageRoot 'examples') -File |
    Where-Object Extension -in '.json', '.jsonl')
if ($exampleFiles.Count -eq 0) { throw 'No P01 examples found.' }
foreach ($file in $exampleFiles) {
    $schemaPath = Join-Path $coverageRoot "schemas/$($file.BaseName).schema.json"
    $schema = Get-Content -LiteralPath $schemaPath -Raw | ConvertFrom-Json -AsHashtable
    if ($schema['$schema'] -ne 'https://json-schema.org/draft/2020-12/schema') {
        throw "Unexpected JSON Schema dialect: $($file.Name)"
    }
    $bundled = Expand-LocalSchema $schema | ConvertTo-Json -Depth 100 -Compress
    $records = if ($file.Extension -eq '.jsonl') {
        @(Get-Content -LiteralPath $file.FullName)
    } else {
        @(Get-Content -LiteralPath $file.FullName -Raw)
    }
    foreach ($record in $records) {
        if (-not (Test-Json -Json $record -Schema $bundled -ErrorAction Stop)) {
            throw "Invalid P01 design example: $($file.Name)"
        }
        $recordCount++
    }
}
[ordered]@{
    powershell_version = $PSVersionTable.PSVersion.ToString()
    powershell_files_parsed = $psFiles.Count
    example_files = $exampleFiles.Count
    design_records_validated = $recordCount
    scope = 'P01 record structure only; no coverage calculation or live API'
} | ConvertTo-Json -Compress
