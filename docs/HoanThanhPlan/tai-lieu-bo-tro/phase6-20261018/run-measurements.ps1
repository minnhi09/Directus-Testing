$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
$protocol = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'protocol-v1.json') -Raw | ConvertFrom-Json
$freeze = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'measurement-source-freeze.json') -Raw | ConvertFrom-Json
$ids = @($protocol.primary_experiment.planned_run_ids)
foreach ($run in $ids) {
    if (Test-Path -LiteralPath (Join-Path $labRoot "artifacts/runs/$run")) {
        throw "Run already exists: $run. Preserve evidence; use a new protocol for another batch."
    }
}
$savedProfile = $env:LAB_RUNTIME_PROFILE
$savedRun = $env:LAB_RUN_ID
$savedBudget = $env:LAB_DETERMINISTIC_MAX_TIME
$savedRate = $env:LAB_RATE_LIMIT
$savedTimeout = $env:LAB_REQUEST_TIMEOUT
try {
    $env:LAB_RUNTIME_PROFILE = 'phase6-20261018'
    $env:LAB_DETERMINISTIC_MAX_TIME = '120'
    $env:LAB_RATE_LIMIT = '5/s'
    $env:LAB_REQUEST_TIMEOUT = '10'
    foreach ($run in $ids) {
        foreach ($entry in $freeze.files) {
            if ((Get-FileHash -LiteralPath (Join-Path $labRoot $entry.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
                throw "Measurement source changed: $($entry.path)"
            }
        }
        $env:LAB_RUN_ID = $run
        $selection = if ($run.EndsWith('-all')) { 'exhaustive' } else { 'pairwise' }
        $started = [DateTimeOffset]::UtcNow.ToString('o')
        $timer = [Diagnostics.Stopwatch]::StartNew()
        & (Join-Path $labRoot 'scripts/run-lab.ps1') test cost-query --set $selection
        $resultCode = $LASTEXITCODE
        $timer.Stop()
        $measurement = [ordered]@{ run_id=$run; started_at=$started; finished_at=[DateTimeOffset]::UtcNow.ToString('o');
            elapsed_seconds=$timer.Elapsed.TotalSeconds; exit_code=$resultCode;
            includes='PowerShell launcher, validation, shared setup, Python runner, restore, metadata';
            excludes='one-time doctor/seed/export, code/model design, analysis, human effort' }
        $timingPath = Join-Path $labRoot "artifacts/runs/$run/invocation-timing.json"
        [IO.File]::WriteAllText($timingPath, ($measurement | ConvertTo-Json -Depth 5), [Text.UTF8Encoding]::new($false))
        if ($resultCode -ne 0) { throw "Measurement failed: $run (exit $resultCode); dependent trials stopped." }
        Write-Output "MEASURED $run : $($timer.Elapsed.TotalSeconds) seconds"
    }
} finally {
    $env:LAB_RUNTIME_PROFILE = $savedProfile
    $env:LAB_RUN_ID = $savedRun
    $env:LAB_DETERMINISTIC_MAX_TIME = $savedBudget
    $env:LAB_RATE_LIMIT = $savedRate
    $env:LAB_REQUEST_TIMEOUT = $savedTimeout
}
