$SERVICE_NAME = Read-Host "What's your service name?"
$SERVICE_DESCRIPTION = Read-Host "What's your service description?"

Write-Host "Setting service name to: $SERVICE_NAME..."

$kebab_case_service_name = $SERVICE_NAME.ToLower() -replace ' ', '-'

(Get-Content pyproject.toml) `
  -replace 'name = "fastapi-template"', "name = `"$kebab_case_service_name`"" |
  Set-Content pyproject.toml

(Get-Content pyproject.toml) `
  -replace 'description = "fastapi-template description"', "description = `"$SERVICE_DESCRIPTION`"" |
  Set-Content pyproject.toml

Get-ChildItem files/config/*.yaml | ForEach-Object {
    (Get-Content $_.FullName) `
      -replace '  name: FastAPI Template', "  name: $SERVICE_NAME" |
      Set-Content $_.FullName
}

if (Test-Path scripts/init.sh) {
    Remove-Item scripts/init.sh
}
if (Test-Path scripts/init.ps1) {
    Remove-Item scripts/init.ps1
}

Write-Host ""
Write-Host "Initialization complete, you're all set!"
Write-Host "Note: Install dependencies on your own, we don't want to mess with how you manage your environment."
