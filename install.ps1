# ============================================================
# install.ps1 — Cài đặt skill Daily-Weather-Brief
#
# Chạy file này để copy skill vào thư mục ~/.claude/skills/
# Sau khi cài, dùng lệnh: /daily-weather-brief Hanoi
# ============================================================

$ErrorActionPreference = "Stop"

$source      = $PSScriptRoot
$destination = Join-Path $HOME ".claude\skills\Daily-Weather-Brief"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Cai dat skill: Daily-Weather-Brief" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Tao thu muc dich neu chua co
if (-not (Test-Path $destination)) {
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Write-Host "  [+] Da tao thu muc: $destination" -ForegroundColor Green
} else {
    Write-Host "  [~] Thu muc da ton tai: $destination" -ForegroundColor Yellow
}

# Copy toan bo file (tru outputs/ va __pycache__)
$excludeDirs = @("outputs", "__pycache__")

Get-ChildItem -Path $source -Recurse | Where-Object {
    $relativePath = $_.FullName.Substring($source.Length + 1)
    $topLevel = $relativePath.Split([IO.Path]::DirectorySeparatorChar)[0]
    $topLevel -notin $excludeDirs -and $_.Name -ne "install.ps1"
} | ForEach-Object {
    $relativePath = $_.FullName.Substring($source.Length + 1)
    $destPath     = Join-Path $destination $relativePath

    if ($_.PSIsContainer) {
        if (-not (Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        }
    } else {
        $destDir = Split-Path $destPath -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $_.FullName -Destination $destPath -Force
        Write-Host "  [+] $relativePath" -ForegroundColor Gray
    }
}

# Tao thu muc outputs/ tai dich (khong copy noi dung)
$outputsDest = Join-Path $destination "outputs"
if (-not (Test-Path $outputsDest)) {
    New-Item -ItemType Directory -Path $outputsDest -Force | Out-Null
    Write-Host "  [+] outputs/ (thu muc trong)" -ForegroundColor Gray
}

# Kiem tra API key
Write-Host ""
Write-Host "--------------------------------------------------" -ForegroundColor DarkGray
$apiKey = $env:OPENWEATHERMAP_API_KEY
if ($apiKey) {
    Write-Host "  [OK] OPENWEATHERMAP_API_KEY da duoc set." -ForegroundColor Green
} else {
    Write-Host "  [!!] OPENWEATHERMAP_API_KEY chua duoc set." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Chay lenh nay de set (thay bang key cua ban):" -ForegroundColor Yellow
    Write-Host '  [Environment]::SetEnvironmentVariable("OPENWEATHERMAP_API_KEY", "your_key", "User")' -ForegroundColor Yellow
}

Write-Host "--------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Cai dat hoan tat!" -ForegroundColor Green
Write-Host "  Su dung: /daily-weather-brief Hanoi" -ForegroundColor Cyan
Write-Host ""
