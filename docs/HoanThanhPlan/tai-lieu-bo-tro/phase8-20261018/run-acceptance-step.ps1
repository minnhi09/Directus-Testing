param(
    [Parameter(Mandatory=$true)][string]$Label,
    [Parameter(Mandatory=$true)][string[]]$LabArguments
)
$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
if ($Label -notmatch '^[a-z0-9-]+$') { throw 'Invalid step label' }
$freeze = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'checkpoint-manifest.json') -Raw | ConvertFrom-Json
foreach ($entry in $freeze.files) {
    $path = Join-Path $labRoot $entry.path
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
        throw "Acceptance input changed: $($entry.path)"
    }
}
$runId = "p8-20261018-$Label"
$saved = @{}
$names = @('LAB_RUNTIME_PROFILE','LAB_RUN_ID','LAB_DETERMINISTIC_MAX_TIME','LAB_RATE_LIMIT','LAB_REQUEST_TIMEOUT','LAB_MAX_TIME','LAB_MAX_EXAMPLES','LAB_CAMPAIGN_SEEDS','LAB_WORKERS')
foreach ($name in $names) { $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
$resultCode = 1
try {
    $env:LAB_RUNTIME_PROFILE = 'phase8-20261018'
    $env:LAB_RUN_ID = $runId
    $env:LAB_DETERMINISTIC_MAX_TIME = '600'
    $env:LAB_RATE_LIMIT = '5/s'
    $env:LAB_REQUEST_TIMEOUT = '10'
    $env:LAB_WORKERS = '1'
    $env:LAB_CAMPAIGN_SEEDS = '101'
    $env:LAB_MAX_TIME = '60'
    $env:LAB_MAX_EXAMPLES = '10'
    $started = [DateTimeOffset]::UtcNow.ToString('o')
    $timer = [Diagnostics.Stopwatch]::StartNew()
    & (Join-Path $labRoot 'scripts/run-lab.ps1') @LabArguments
    $resultCode = $LASTEXITCODE
    $timer.Stop()
    $timing = [ordered]@{ run_id=$runId; started_at=$started; finished_at=[DateTimeOffset]::UtcNow.ToString('o');
        elapsed_seconds=$timer.Elapsed.TotalSeconds; exit_code=$resultCode; command=$LabArguments;
        note='Native raw/guided overrides are short compatibility probes only; historical main campaign budgets remain 1200s/100 examples/3 seeds.' }
    $path = Join-Path $labRoot "artifacts/runs/$runId/acceptance-invocation.json"
    if (Test-Path -LiteralPath (Split-Path -Parent $path)) {
        [IO.File]::WriteAllText($path, ($timing | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
    }
} finally {
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
}
exit $resultCode
