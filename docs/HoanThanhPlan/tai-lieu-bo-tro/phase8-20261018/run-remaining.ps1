$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
$steps = @(
    @{ label='query-full'; arguments=@('test','cost-query','--set','exhaustive'); outcomes='component-outcomes.json' },
    @{ label='scenarios'; arguments=@('test','scenarios'); outcomes='scenario-outcomes.json' },
    @{ label='smoke'; arguments=@('smoke'); outcomes='component-outcomes.json' },
    @{ label='invariants'; arguments=@('test','invariants'); outcomes='component-outcomes.json' },
    @{ label='replay-qfqspn'; arguments=@('replay','qfqspn'); outcomes='component-outcomes.json'; portable=$true },
    @{ label='replay-z6ynal'; arguments=@('replay','Z6yNal'); outcomes='component-outcomes.json'; portable=$true },
    @{ label='projection-replay'; arguments=@('replay','P3-CONTRACT-PROJECTION'); outcomes='component-outcomes.json' }
)
$originalReplay = $env:LAB_REPLAY_EVENTS
$overall = 0
$records = @()
try {
    foreach ($step in $steps) {
        if ($step.portable) { $env:LAB_REPLAY_EVENTS='phase8-portable-input/guided/seed-101/schemathesis-events.ndjson' }
        else { $env:LAB_REPLAY_EVENTS=$originalReplay }
        & (Join-Path $PSScriptRoot 'run-acceptance-step.ps1') -Label $step.label -LabArguments $step.arguments | Out-Null
        $stepCode = $LASTEXITCODE
        if ($stepCode -ne 0) { $overall = $stepCode }
        $base = Join-Path $labRoot "artifacts/runs/p8-20261018-$($step.label)"
        $outcomePath = Join-Path $base $step.outcomes
        if (-not (Test-Path -LiteralPath $outcomePath)) { throw "Missing restore outcome: $($step.label); stop dependent mutation" }
        $outcomes = Get-Content -LiteralPath $outcomePath -Raw | ConvertFrom-Json
        if ($outcomes.restore_exit_code -ne 0) { throw "Restore failed: $($step.label); stop dependent mutation" }
        foreach ($reportName in @('designed-report.json','invariant-report.json')) {
            $reportPath = Join-Path $base $reportName
            if (Test-Path -LiteralPath $reportPath) {
                $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
                if ($report.setup_status -ne 'passed' -or @($report.selected_not_run).Count -gt 0) { throw "Preflight/incomplete run: $($step.label); investigate before continuing" }
                foreach ($case in $report.cases) {
                    if ($case.cleanup_status -ne 'passed' -or $case.status -in @('blocked','incomplete') -or ($case.error_type -and $case.error_type -ne 'AssertionError')) {
                        throw "Unsafe or harness failure: $($step.label)/$($case.id); investigate before continuing"
                    }
                }
            }
        }
        $records += @{ label=$step.label; exit_code=$stepCode; restore_exit_code=$outcomes.restore_exit_code }
        $summary = @{ collection_complete=$false; contains_failed_assertions=($overall -ne 0); steps=$records }
        [IO.File]::WriteAllText((Join-Path $PSScriptRoot 'remaining-steps.json'), ($summary | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
        Write-Output "RECORDED $($step.label): exit=$stepCode restore=$($outcomes.restore_exit_code)"
    }
    $summary = @{ collection_complete=$true; contains_failed_assertions=($overall -ne 0); steps=$records; aggregate_exit_code=$overall }
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot 'remaining-steps.json'), ($summary | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
} finally {
    $env:LAB_REPLAY_EVENTS=$originalReplay
}
# Evidence collection may finish while SUT assertions fail. Keep nonzero visible.
exit $overall
