# Scope: P09 private namespace directory + p09.env only. Never read credentials.
[CmdletBinding()]
param(
    [ValidateSet('Check','Harden','Restore')][string]$Mode = 'Check',
    [Parameter(Mandatory)][ValidatePattern('^r06-k05-p09-[a-z0-9][a-z0-9-]{0,35}$')][string]$Namespace,
    [string]$RunnerSid,
    [string]$BackupPath
)
$ErrorActionPreference = 'Stop'
$ciRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$ciDirectory = Join-Path $ciRoot "runtime/profiles/$Namespace"
$ciEnvPath = Join-Path $ciDirectory 'p09.env'
$ciTargets = @($ciDirectory, $ciEnvPath)
$ciSecurityRoot = Join-Path $ciRoot 'runtime/security'
$ciRunner = if ($RunnerSid) { [Security.Principal.SecurityIdentifier]::new($RunnerSid) } else { [Security.Principal.WindowsIdentity]::GetCurrent().User }
$ciAllowed = @($ciRunner.Value, 'S-1-5-18', 'S-1-5-32-544')
try {
    if (-not $IsWindows) { throw 'NTFS_REQUIRED' }
    foreach ($ciPath in $ciTargets) {
        $ciItem = Get-Item -LiteralPath $ciPath -Force
        if (($ciItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_TARGET' }
    }
    # Reject junction/symlink ancestors under this repository as well.
    $ciAncestor = Get-Item -LiteralPath $ciDirectory
    while ($ciAncestor.FullName -ne $ciRoot) {
        if (($ciAncestor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_PARENT' }
        $ciAncestor = $ciAncestor.Parent
        if (-not $ciAncestor) { throw 'OUTSIDE_ROOT' }
    }
    if ($Mode -ne 'Check') {
        if (-not $BackupPath) { throw 'EXPLICIT_BACKUP_REQUIRED' }
        $ciBackup = [IO.Path]::GetFullPath($BackupPath)
        if (-not $ciBackup.StartsWith($ciSecurityRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'BACKUP_OUTSIDE_PRIVATE_SECURITY_DIR' }
        if ($Mode -eq 'Harden') {
            if (Test-Path -LiteralPath $ciBackup) { throw 'BACKUP_ALREADY_EXISTS' }
            New-Item -ItemType Directory -Path (Split-Path -Parent $ciBackup) -Force | Out-Null
            $ciOriginal = @{}
            foreach ($ciPath in $ciTargets) {
                $ciOriginal[(Split-Path -Leaf $ciPath)] = (Get-Acl -LiteralPath $ciPath).GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)
            }
            @{ namespace=$Namespace; directory_dacl=$ciOriginal[$Namespace]; env_dacl=$ciOriginal['p09.env'] } | ConvertTo-Json | Set-Content -LiteralPath $ciBackup -Encoding utf8
            foreach ($ciPath in @($ciTargets + $ciBackup)) {
                $ciAcl = Get-Acl -LiteralPath $ciPath
                $ciAcl.SetAccessRuleProtection($true, $false)
                foreach ($ciRule in @($ciAcl.GetAccessRules($true, $false, [Security.Principal.SecurityIdentifier]))) {
                    if ($ciRule.AccessControlType -eq 'Allow' -and $ciRule.IdentityReference.Value -notin $ciAllowed) { $ciAcl.RemoveAccessRuleSpecific($ciRule) }
                }
                $ciInheritance = if ($ciPath -eq $ciDirectory) { [Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit' } else { [Security.AccessControl.InheritanceFlags]::None }
                foreach ($ciSid in $ciAllowed) {
                    $ciRule = [Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new($ciSid), [Security.AccessControl.FileSystemRights]::FullControl, $ciInheritance, [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
                    $ciAcl.SetAccessRule($ciRule)
                }
                Set-Acl -LiteralPath $ciPath -AclObject $ciAcl
            }
        } else {
            $ciRestore = Get-Content -LiteralPath $ciBackup -Raw | ConvertFrom-Json
            if ($ciRestore.namespace -ne $Namespace) { throw 'BACKUP_NAMESPACE_MISMATCH' }
            foreach ($ciPath in $ciTargets) {
                $ciAcl = Get-Acl -LiteralPath $ciPath
                $ciDacl = if ($ciPath -eq $ciDirectory) { $ciRestore.directory_dacl } else { $ciRestore.env_dacl }
                $ciAcl.SetSecurityDescriptorSddlForm($ciDacl, [Security.AccessControl.AccessControlSections]::Access)
                Set-Acl -LiteralPath $ciPath -AclObject $ciAcl
            }
        }
    }
    $ciCounts = @{}
    $ciProtected = $true
    foreach ($ciPath in $ciTargets) {
        $ciAcl = Get-Acl -LiteralPath $ciPath
        $ciRules = @($ciAcl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) | Where-Object {
            $_.AccessControlType -eq 'Allow' -and ($_.PropagationFlags -band [Security.AccessControl.PropagationFlags]::InheritOnly) -eq 0 -and $_.IdentityReference.Value -notin $ciAllowed
        })
        $ciCounts[(Split-Path -Leaf $ciPath)] = $ciRules.Count
        $ciProtected = $ciProtected -and $ciAcl.AreAccessRulesProtected
    }
    $ciStream = [IO.File]::Open($ciEnvPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $ciStream.Dispose() # Open succeeds under actual process identity; read zero bytes.
    $ciSafe = $ciProtected -and (@($ciCounts.Values | Where-Object { $_ -ne 0 }).Count -eq 0)
    [ordered]@{ mode=$Mode; status=$(if ($ciSafe) {'PASS'} else {'BLOCKED_PRIVATE_ACL'}); namespace=$Namespace; broad_allow_rules=$ciCounts; inheritance_disabled=$ciProtected; current_identity_can_open_profile=$true; secret_bytes_read=0; credential_content_changed=$false; scope='P09_NAMESPACE_DIRECTORY_AND_ENV_ONLY' } | ConvertTo-Json -Compress
    if ($ciSafe) { exit 0 } else { exit 2 }
} catch {
    # Do not render exception strings, credentials, SDDL or machine account names.
    @{ mode=$Mode; status='BLOCKED_PRIVATE_ACL'; error_type=$_.Exception.GetType().Name; credential_content_changed=$false } | ConvertTo-Json -Compress
    exit 2
}
