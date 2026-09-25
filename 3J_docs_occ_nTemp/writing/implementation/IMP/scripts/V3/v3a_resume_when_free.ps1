# Waits until memory is free, then resumes the 15 unfinished V3a tasks with the RAM guard.
# Start condition: (no fleet06c python process AND RAM used < 60 %) OR RAM used < 50 %.
# Gives up after 8 hours without starting. Logs to the V3a _logs folder.
$base = "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp"
$camp = "$base\Leg3_4-split\Step8_docs\campaign_local_P10R_V3a"
$log  = "$camp\_logs\resume_waiter.log"
function L($m) { $s = "{0} {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $m; Add-Content -Path $log -Value $s -Encoding utf8; Write-Output $s }
L "[waiter] start"
$deadline = (Get-Date).AddHours(8)
while ((Get-Date) -lt $deadline) {
  $os = Get-CimInstance Win32_OperatingSystem
  $used = 100.0 * (1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize)
  $fleet = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*fleet06c*' }).Count
  $mine = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*campaign_local_P10R_V3a*' -and $_.ProcessId -ne $PID }).Count
  if ($mine -gt 0) { L "[waiter] V3a processes already present ($mine); not starting a duplicate; exit 3"; exit 3 }
  if ((($fleet -eq 0) -and ($used -lt 60)) -or ($used -lt 50)) {
    L ("[waiter] GO used={0:N1}% fleet={1}" -f $used, $fleet)
    $drv = Start-Process -FilePath "py" -ArgumentList @("-3","-u","$base\writing\implementation\IMP\scripts\V3\v3a_local_driver.py","$camp","--max-par","10","--ids","6,7,8,9,20,21,22,23,24,25,26,27,28,29,39") -RedirectStandardOutput "$camp\_logs\driver_resume_stdout.txt" -RedirectStandardError "$camp\_logs\driver_resume_stderr.txt" -WindowStyle Hidden -PassThru
    L ("[waiter] driver pid={0}" -f $drv.Id)
    Start-Sleep -Seconds 90
    $wd = Start-Process -FilePath "powershell" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$base\writing\implementation\IMP\scripts\p10r_mem_watchdog.ps1","-Threshold","80","-IntervalS","15","-Log","$camp\_logs\watchdog.log") -WindowStyle Hidden -PassThru
    L ("[waiter] watchdog pid={0}; exit 0" -f $wd.Id)
    exit 0
  }
  L ("[waiter] wait used={0:N1}% fleet={1}" -f $used, $fleet)
  Start-Sleep -Seconds 120
}
L "[waiter] gave up after 8 h; exit 4"
exit 4
