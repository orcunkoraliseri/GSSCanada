$ErrorActionPreference = "Continue"
Set-Location "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step5_docs"
$steps = @("--full", "--aggregate", "--bem", "--exclusion", "--regression")
foreach ($s in $steps) {
    Write-Output "===== STEP5 $s START $(Get-Date -Format o) ====="
    py -3 3rdJ_05_censusLinkage_2split.py $s
    $rc = $LASTEXITCODE
    Write-Output "===== STEP5 $s END $(Get-Date -Format o) exit=$rc ====="
    if ($rc -ne 0) {
        Write-Output "ABORTING: $s failed with exit code $rc"
        exit $rc
    }
}
Write-Output "===== ALL STEP5 SUBSTEPS COMPLETE $(Get-Date -Format o) ====="
