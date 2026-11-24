$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$bashPath = if ($env:LAB_GIT_BASH) { $env:LAB_GIT_BASH } else { Join-Path $env:ProgramFiles 'Git/bin/bash.exe' }
$jqPath = if ($env:LAB_JQ_EXE) { $env:LAB_JQ_EXE } else { Join-Path $labRoot 'runtime/tools/jq-1.8.2.exe' }
$expectedHash = 'a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627'
if (-not (Test-Path -LiteralPath $bashPath -PathType Leaf)) { throw 'Git Bash missing; install Git for Windows or set LAB_GIT_BASH.' }
if (-not (Test-Path -LiteralPath $jqPath -PathType Leaf)) { throw 'jq missing; run .\scripts\setup-windows.ps1 first.' }
if ((Get-FileHash -LiteralPath $jqPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { throw 'jq checksum mismatch.' }
$savedPath = $env:PATH
$savedJq = $env:LAB_JQ_EXE
$labExitCode = 1
Push-Location -LiteralPath $labRoot
try {
    $env:PATH = "$(Join-Path $PSScriptRoot 'windows');$savedPath"
    $env:LAB_JQ_EXE = $jqPath.Replace('\', '/')
    if ($args.Count -gt 0) { $labArguments = @($args) } else { $labArguments = @('doctor') }
    & $bashPath -c 'exec bash lab.sh "$@"' lab @labArguments
    $labExitCode = $LASTEXITCODE
} finally {
    $env:PATH = $savedPath
    $env:LAB_JQ_EXE = $savedJq
    Pop-Location
}
exit $labExitCode
