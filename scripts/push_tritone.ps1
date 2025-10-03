param(
  [string]$RepoPath = "C:\spotify api",
  [string]$Branch = "tritone-task",
  [string]$RemoteUrl = "https://github.com/geetmehta989/spotify-api.git"
)
$ErrorActionPreference = 'Stop'

# Ensure Git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "Git is not installed or not in PATH."
  exit 1
}

# Validate path
if (-not (Test-Path -LiteralPath $RepoPath)) {
  Write-Error "Project path not found: $RepoPath"
  exit 1
}

# Move into repo
Set-Location -LiteralPath $RepoPath

# Initialize if needed
if (-not (Test-Path .git)) {
  git init
}

# Ensure .env is ignored and not staged
if (Test-Path .gitignore) {
  $ignore = Get-Content .gitignore -Raw
  if ($ignore -notmatch '(?m)^\s*\.env\s*$') {
    Add-Content .gitignore "`n.env`n"
  }
} else {
  Set-Content .gitignore ".env`n"
}
# Unstage .env if it was staged previously
try { git rm --cached .env 2>$null | Out-Null } catch {}

# Create/switch branch
$null = git checkout -B $Branch 2>$null

# Configure remote
if ((git remote) -contains "origin") {
  git remote set-url origin $RemoteUrl
} else {
  git remote add origin $RemoteUrl
}

# Stage and commit
git add -A
$commitMsg = "chore: add Tritone project files and automation"
$null = git commit -m $commitMsg 2>$null; if ($LASTEXITCODE -ne 0) { Write-Host "No changes to commit (continuing)." }

# Validate token
if (-not $env:GITHUB_TOKEN -or $env:GITHUB_TOKEN -eq 'YOUR_PAT_HERE') {
  Write-Error "Please set $env:GITHUB_TOKEN to a valid GitHub PAT before running."
  exit 1
}

# Push using header auth (HTTPS)
$pushCmd = @(
  '-c', "http.extraheader=AUTHORIZATION: bearer $env:GITHUB_TOKEN",
  'push', '-u', 'origin', "HEAD:$Branch"
)
& git @pushCmd

if ($LASTEXITCODE -ne 0) {
  Write-Error "Push failed. Check token permissions (repo:write) and remote URL."
  exit 1
}

Write-Host "`n✅ Push complete."
Write-Host "Deployment link: https://github.com/geetmehta989/spotify-api/tree/$Branch"
