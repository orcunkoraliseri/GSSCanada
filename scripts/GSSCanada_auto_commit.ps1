$repoRoot  = "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
$git       = "C:\Users\o_iseri\AppData\Local\Programs\Git\cmd\git.exe"
$logDir    = Join-Path $repoRoot "tmp"
$logFile   = Join-Path $logDir  "auto_commit.log"
$date      = Get-Date -Format "yyyy-MM-dd"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

Set-Location $repoRoot

& $git add -A

$status = & $git status --porcelain
if (-not $status) {
    Add-Content -Path $logFile -Value "[$timestamp] Nothing to commit"
    exit 0
}

& $git commit -m "chore: auto daily commit $date"
if ($LASTEXITCODE -ne 0) {
    Add-Content -Path $logFile -Value "[$timestamp] COMMIT FAILED (exit $LASTEXITCODE)"
    exit 1
}

& $git push origin windows-dev
if ($LASTEXITCODE -eq 0) {
    Add-Content -Path $logFile -Value "[$timestamp] SUCCESS"
} else {
    Add-Content -Path $logFile -Value "[$timestamp] PUSH FAILED (exit $LASTEXITCODE)"
    exit 1
}
