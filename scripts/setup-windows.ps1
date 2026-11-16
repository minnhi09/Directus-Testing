[CmdletBinding()]
param([string]$JqSourcePath)
$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$toolDir = Join-Path $labRoot 'runtime/tools'
$target = Join-Path $toolDir 'jq-1.8.2.exe'
$expectedHash = 'a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627'
$downloadUrl = 'https://github.com/jqlang/jq/releases/download/jq-1.8.2/jq-windows-amd64.exe'
if (-not [Environment]::Is64BitOperatingSystem) { throw 'This bootstrap requires Windows x64.' }
New-Item -ItemType Directory -Force -Path $toolDir | Out-Null
if (-not (Test-Path -LiteralPath $target)) {
    $temporary = Join-Path $toolDir ('jq-' + [Guid]::NewGuid().ToString('N') + '.download')
    try {
        if ($JqSourcePath) { Copy-Item -LiteralPath $JqSourcePath -Destination $temporary }
        else { Invoke-WebRequest -Uri $downloadUrl -OutFile $temporary -UseBasicParsing }
        if ((Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
            throw 'jq checksum mismatch; downloaded executable will not be used.'
        }
        Move-Item -LiteralPath $temporary -Destination $target
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
    }
}
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
    throw 'Existing jq checksum mismatch; refusing to execute it.'
}
& $target --version
if ($LASTEXITCODE -ne 0) { throw 'jq executable did not start.' }
Write-Output 'jq ready in runtime/tools; no global PATH or package settings changed.'
