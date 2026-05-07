$taskName = "GSSCanada-AutoCommit"
$script   = "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\scripts\GSSCanada_auto_commit.ps1"

$action = New-ScheduledTaskAction `
    -Execute  "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""

$trigger = New-ScheduledTaskTrigger -Daily -At "22:50"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$principal = New-ScheduledTaskPrincipal `
    -UserId   "TABLETOP1\umroot" `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName  $taskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -Principal $principal `
    -Force

Write-Host "Registered: '$taskName' - runs daily at 22:50 while logged in."
