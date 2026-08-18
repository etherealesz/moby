$PACKAGE_NAME = Read-Host "What's your package name?"

Write-Host "Setting package name to: $PACKAGE_NAME..."

(Get-Content package.json) `
  -replace '"name": ".*"', "`"name`": `"$PACKAGE_NAME`"" |
  Set-Content package.json

$paths = @(
    "node_modules",
    "bun.lock",
    "bun.block",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse
    }
}

Write-Host "Reinstalling dependencies..."

bun install

if (Test-Path scripts/init.sh) {
    Remove-Item scripts/init.sh
}

if (Test-Path scripts/init.ps1) {
    Remove-Item scripts/init.ps1
}

Write-Host "Initialization complete, you're all set!"