$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
$previous = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'remaining-steps.json') -Raw | ConvertFrom-Json
if (-not $previous.collection_complete) { throw 'Previous suite/replay work is not complete; do not overlap DB mutation' }
$records = @()
$overall = 0
foreach ($profile in @('raw','guided')) {
    & (Join-Path $PSScriptRoot 'run-acceptance-step.ps1') -Label "probe-$profile" -LabArguments @('test',$profile) | Out-Null
    $resultCode = $LASTEXITCODE
    if ($resultCode -ne 0) { $overall = $resultCode }
    $base = Join-Path $labRoot "artifacts/runs/p8-20261018-probe-$profile"
    $indexPath = Join-Path $base 'campaign-index.json'
    if (-not (Test-Path -LiteralPath $indexPath)) { throw "Missing campaign index: $profile" }
    $index = Get-Content -LiteralPath $indexPath -Raw | ConvertFrom-Json
    if (@($index.campaigns).Count -ne 1) { throw "Wrong probe seed count: $profile" }
    $campaign = $index.campaigns[0]
    if ($campaign.restore_exit_code -ne 0 -or -not $campaign.report_present -or -not $campaign.coverage_present) {
        throw "Setup/report/restore failure: $profile; stop dependent probe"
    }
    $records += @{ profile=$profile; run_id="p8-20261018-probe-$profile"; exit_code=$resultCode;
        restore_exit_code=$campaign.restore_exit_code; termination=$campaign.termination;
        tested_operations=$campaign.schemathesis.operations.tested; budget=$campaign.budget }
    Write-Output "RECORDED probe-$profile : exit=$resultCode restore=$($campaign.restore_exit_code) stop=$($campaign.termination)"
}
$record = @{ collection_complete=$true; aggregate_exit_code=$overall; probes=$records;
    scope='Current checkpoint compatibility only: 60s, max-examples10, seed101 per profile. Historical three-seed main campaigns remain separate at 1200s/max-examples100.' }
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'pipeline-probes.json'), ($record | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
exit $overall
