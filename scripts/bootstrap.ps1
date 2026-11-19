$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== AI Desktop Bootstrap ==="
Write-Host ""

# ----------------------------------------------------
# Winget
# ----------------------------------------------------

if (-not (Get-Command winget -ErrorAction SilentlyContinue))
{
    Write-Error "Winget not found"
    exit 1
}

# ----------------------------------------------------
# Go
# ----------------------------------------------------

# Go is installed from the official package; the build only needs any Go
# >= 1.26 on PATH; see docs/environment.md.
if (-not (Get-Command go -ErrorAction SilentlyContinue))
{
    winget install --id GoLang.Go `
        --accept-source-agreements `
        --accept-package-agreements `
        --silent
}

# ----------------------------------------------------
# CMake
# ----------------------------------------------------

winget install --id Kitware.CMake `
    --accept-source-agreements `
    --accept-package-agreements `
    --silent

# ----------------------------------------------------
# Ninja
# ----------------------------------------------------

winget install --id Ninja-build.Ninja `
    --accept-source-agreements `
    --accept-package-agreements `
    --silent

# ----------------------------------------------------
# Refresh PATH
# ----------------------------------------------------

# winget installs are not visible in the current session.
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path", "User")

# ----------------------------------------------------
# Go Proxy (China)
# ----------------------------------------------------

if (-not (Get-Command go -ErrorAction SilentlyContinue))
{
    Write-Error "go still not on PATH. Open a new shell and re-run, or install Go 1.26+ manually."
    exit 1
}

go env -w GOPROXY=https://goproxy.cn,direct

# ----------------------------------------------------
# go mod download
# ----------------------------------------------------

Push-Location server

go mod download

Pop-Location

Write-Host ""
Write-Host "Bootstrap finished."
Write-Host ""
Write-Host "Manual steps still required:"
Write-Host "  1. Qt 6.12 via Qt Online Installer"
Write-Host "  2. vcpkg, only if vcpkg.json declares C++ dependencies"
Write-Host "  3. CMakeUserPresets.json, copied from the .example file"
Write-Host ""
Write-Host "See docs/environment.md for details."
Write-Host ""
