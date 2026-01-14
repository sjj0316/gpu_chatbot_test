param(
  [string]$SampleFile = ".env.sample",
  [string]$ProdFile = ".env.prod"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SampleFile)) {
  Write-Host "[FAIL] $SampleFile not found (root standard required)."
  exit 1
}

if (-not (Test-Path $ProdFile)) {
  Write-Host "[FAIL] $ProdFile not found. Provide it before deploy."
  exit 1
}

$sampleLines = Get-Content $SampleFile
$prodLines   = Get-Content $ProdFile

$keys = @()
foreach ($line in $sampleLines) {
  $trim = $line.Trim()
  if ($trim.Length -eq 0) { continue }
  if ($trim.StartsWith("#")) { continue }
  if ($trim -notmatch "^[A-Za-z_][A-Za-z0-9_]*=") { continue }
  $k = $trim.Split("=",2)[0].Trim()
  if ($k.Length -gt 0) { $keys += $k }
}

$missing = @()
foreach ($k in $keys) {
  $match = $prodLines | Where-Object { $_ -match "^$([regex]::Escape($k))=" } | Select-Object -First 1
  if ($null -ne $match) {
    $val = $match.Split("=",2)[1]
    if ([string]::IsNullOrWhiteSpace($val)) {
      $missing += $k
    }
  } else {
    $envVal = [Environment]::GetEnvironmentVariable($k)
    if ([string]::IsNullOrWhiteSpace($envVal)) {
      $missing += $k
    }
  }
}

# Explicit TAG check (must exist in .env.prod or environment)
$tagLine = $prodLines | Where-Object { $_ -match "^TAG=" } | Select-Object -First 1
if ($null -eq $tagLine -and [string]::IsNullOrWhiteSpace($env:TAG)) {
  $missing += "TAG"
}

if ($missing.Count -gt 0) {
  Write-Host "[FAIL] Missing required env keys (names only):"
  $missing | ForEach-Object { Write-Host " - $_" }
  exit 1
}

Write-Host "[OK] Required env keys are present (values not displayed)."
