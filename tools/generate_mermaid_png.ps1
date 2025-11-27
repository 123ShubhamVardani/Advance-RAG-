<#
Generate PNG/SVG from Mermaid source using mermaid-cli (mmdc).
Requires Node + mermaid-cli:
  npm install -g @mermaid-js/mermaid-cli
Usage:
  powershell -ExecutionPolicy Bypass -File tools/generate_mermaid_png.ps1 -Input architecture.mmd -OutDir dist
#>
param(
  [string]$Input = "architecture.mmd",
  [string]$OutDir = "dist",
  [switch]$Dark
)

if (-not (Get-Command mmdc -ErrorAction SilentlyContinue)) {
  Write-Host "mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli" -ForegroundColor Yellow
  exit 1
}

if (-not (Test-Path $Input)) {
  Write-Host "Input file not found: $Input" -ForegroundColor Red
  exit 1
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$theme = if ($Dark) { 'dark' } else { 'default' }
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($Input)

$png = Join-Path $OutDir "$baseName-mermaid-$theme.png"
$svg = Join-Path $OutDir "$baseName-mermaid-$theme.svg"

mmdc -i $Input -o $png -t $theme
mmdc -i $Input -o $svg -t $theme

Write-Host "Generated: $png" -ForegroundColor Green
Write-Host "Generated: $svg" -ForegroundColor Green
