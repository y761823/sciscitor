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
# Mise
# ----------------------------------------------------

winget install --id jdx.mise `
    --accept-source-agreements `
    --accept-package-agreements `
    --silent

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
# mise install
# ----------------------------------------------------

mise install

# ----------------------------------------------------
# Go Proxy (China)
# ----------------------------------------------------

# go comes from mise and is not on PATH in non-interactive shells,
# so invoke it through 'mise exec'.
mise exec -- go env -w GOPROXY=https://goproxy.cn,direct

# ----------------------------------------------------
# go mod download
# ----------------------------------------------------

Push-Location server

mise exec -- go mod download

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
