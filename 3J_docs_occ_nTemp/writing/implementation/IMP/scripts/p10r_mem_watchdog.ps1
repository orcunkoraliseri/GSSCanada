# p10r_mem_watchdog.ps1 -- RAM guard for the LOCAL P10R campaign (2026-09-24).
# The author reaches this box only via Parsec and cannot reboot it: a RAM freeze = locked out.
# Every -IntervalS seconds reads physical memory in use; if it is >= -Threshold percent on two
# samples in a row, kills the P10R driver first (so it starts nothing new), then every process whose
# command line contains campaign_local_P10R (cell runners, energyplus -d <cell>/run), logs, exits 2.
# Only processes of THIS campaign are matched; the author's other EnergyPlus / Python work is untouched.
# Exits 0 by itself once no P10R process has been seen for 3 samples in a row (campaign over).
# -DryRun prints WOULD KILL instead of killing (used to see the guard fire at a low threshold).
param(
  [double]$Threshold = 80,
  [int]$IntervalS = 15,
  [string]$Log = "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step8_docs\campaign_local_P10R\_logs\watchdog.log",
  [switch]$DryRun,
  [int]$MaxSamples = 0
)

function Write-Log($msg) {
  $line = "{0} {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $msg
  Write-Output $line
  Add-Content -Path $Log -Value $line -Encoding utf8
}

function Get-Targets {
  Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and ($_.CommandLine -like "*p10r_local_campaign*" -or $_.CommandLine -like "*campaign_local_P10R*") -and
    $_.ProcessId -ne $PID -and $_.CommandLine -notlike "*p10r_mem_watchdog*"
  }
}

Write-Log ("[watchdog] start threshold={0}% interval={1}s dryrun={2}" -f $Threshold, $IntervalS, [bool]$DryRun)
$hot = 0; $idle = 0; $n = 0
while ($true) {
  $n++
  $os = Get-CimInstance Win32_OperatingSystem
  $used = 100.0 * (1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize)
  $targets = @(Get-Targets)
  $ep = @($targets | Where-Object { $_.Name -like "energyplus*" }).Count
  if ($n % 20 -eq 1) { Write-Log ("[watchdog] used={0:N1}% p10r_procs={1} energyplus={2}" -f $used, $targets.Count, $ep) }
  if ($used -ge $Threshold) { $hot++ } else { $hot = 0 }
  if ($hot -ge 2) {
    Write-Log ("[watchdog] FIRED used={0:N1}% >= {1}% on 2 samples; p10r_procs={2}" -f $used, $Threshold, $targets.Count)
    $drivers = $targets | Where-Object { $_.CommandLine -like "*p10r_local_campaign*" }
    $rest = $targets | Where-Object { $_.CommandLine -notlike "*p10r_local_campaign*" }
    foreach ($p in @($drivers) + @($rest)) {
      if ($DryRun) { Write-Log ("[watchdog] WOULD KILL pid={0} {1}" -f $p.ProcessId, $p.Name) }
      else { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue; Write-Log ("[watchdog] KILLED pid={0} {1}" -f $p.ProcessId, $p.Name) }
    }
    exit 2
  }
  if ($targets.Count -eq 0) { $idle++ } else { $idle = 0 }
  if ($idle -ge 3) { Write-Log "[watchdog] no P10R process for 3 samples; campaign over, exiting 0"; exit 0 }
  if ($MaxSamples -gt 0 -and $n -ge $MaxSamples) { Write-Log "[watchdog] MaxSamples reached, exiting 0"; exit 0 }
  Start-Sleep -Seconds $IntervalS
}
