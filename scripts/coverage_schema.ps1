param([Parameter(Mandatory=$true)][string]$Payload)
# Local P01 schemas have already been bundled by coverage_offline.py; no URI fetch.
$ErrorActionPreference = 'Stop'
$data = Get-Content -LiteralPath $Payload -Raw | ConvertFrom-Json -AsHashtable
$errorsFound = @()
foreach ($item in $data) {
    try {
        $valid = Test-Json -Json $item.json -Schema $item.schema -ErrorAction Stop
        if (-not $valid) { $errorsFound += $item.location }
    } catch { $errorsFound += $item.location }
}
ConvertTo-Json -InputObject @($errorsFound) -Compress
if ($errorsFound.Count) { exit 1 }
