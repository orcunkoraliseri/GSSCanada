# assemble.ps1 — build the combined 2J manuscript from the chapter/table/figure sources.
# Concatenates Chapters 00-08 in order, inlines the 5 main tables at their
# *(insert `Table_XX.md` here)* placeholders, and embeds the 16 figures as
# relative-path image links at their *(insert `Figure_XX.png` here)* placeholders.
# Re-run any time a chapter or table changes: powershell -File fullSet\assemble.ps1

$ErrorActionPreference = 'Stop'
$base    = 'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing'
$chDir   = Join-Path $base 'chapters'
$tblDir  = Join-Path $base 'tables'
$tblSIDir= Join-Path $tblDir 'SI'
$outDir  = Join-Path $base 'fullSet'
$outFile = Join-Path $outDir '2J_full_manuscript.md'

$order = @(
  'Chapter_00_FrontMatter.md',
  'Chapter_01_Introduction.md',
  'Chapter_02_Datasets.md',
  'Chapter_03_Methods.md',
  'Chapter_04_ExperimentalDesign.md',
  'Chapter_05_Results.md',
  'Chapter_06_Discussion.md',
  'Chapter_07_Limitations.md',
  'Chapter_08_Conclusion.md'
)

function Get-TablePath($name) {
  $p = Join-Path $tblDir $name
  if (Test-Path $p) { return $p }
  $p2 = Join-Path $tblSIDir $name
  if (Test-Path $p2) { return $p2 }
  return $null
}

function Get-InlineTable($name) {
  $p = Get-TablePath $name
  if (-not $p) { return "*(table file $name not found)*" }
  $lines = Get-Content -LiteralPath $p -Encoding UTF8
  $out = New-Object System.Collections.Generic.List[string]
  foreach ($l in $lines) {
    if ($l -match '^#\s+Table') { continue }       # drop redundant top heading
    if ($l -match '^\*Source:\*') { continue }      # drop internal provenance line
    $out.Add($l)
  }
  while ($out.Count -gt 0 -and $out[0].Trim() -eq '') { $out.RemoveAt(0) }
  while ($out.Count -gt 0 -and $out[$out.Count-1].Trim() -eq '') { $out.RemoveAt($out.Count-1) }
  return ($out -join "`n")
}

$tablePat = '^\*\*(?<lbl>Table \d+)\.\*\* \*\(insert `(?<f>[^`]+)` here\)\*(?<rest>.*)$'
$figPat   = '^\*\*(?<lbl>Figure S?\d+)\.\*\* \*\(insert `(?<f>[^`]+)` here\)\*(?<rest>.*)$'

$result = New-Object System.Collections.Generic.List[string]
$tblCount = 0; $figCount = 0

for ($i=0; $i -lt $order.Count; $i++) {
  $path = Join-Path $chDir $order[$i]
  $lines = Get-Content -LiteralPath $path -Encoding UTF8
  foreach ($line in $lines) {
    $mt = [regex]::Match($line, $tablePat)
    $mf = [regex]::Match($line, $figPat)
    if ($mt.Success) {
      $result.Add("**$($mt.Groups['lbl'].Value).**$($mt.Groups['rest'].Value)")
      $result.Add('')
      $result.Add( (Get-InlineTable $mt.Groups['f'].Value) )
      $result.Add('')
      $tblCount++
    } elseif ($mf.Success) {
      $f = $mf.Groups['f'].Value
      if ($f -match '^Figure_S') { $rel = "../figures/SI/$f" } else { $rel = "../figures/$f" }
      $result.Add("**$($mf.Groups['lbl'].Value).**$($mf.Groups['rest'].Value)")
      $result.Add('')
      $result.Add("![$($mf.Groups['lbl'].Value)]($rel)")
      $result.Add('')
      $figCount++
    } else {
      $result.Add($line)
    }
  }
  if ($i -lt $order.Count-1) { $result.Add(''); $result.Add('---'); $result.Add('') }
}

Set-Content -LiteralPath $outFile -Value ($result -join "`n") -Encoding UTF8
Write-Output "Wrote: $outFile"
Write-Output "Chapters: $($order.Count)  Tables inlined: $tblCount  Figures embedded: $figCount  Lines: $($result.Count)"
