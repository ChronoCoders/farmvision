@echo off
REM FarmVision Release Script for Windows
REM This script helps create a new release with proper tagging

setlocal enabledelayedexpansion

REM Check if version is provided
if "%~1"=="" (
    echo Error: Version number required
    echo.
    echo Usage: create_release.bat ^<version^> [release-type]
    echo.
    echo Examples:
    echo   create_release.bat 1.0.0          # Stable release
    echo   create_release.bat 1.0.0 beta     # Beta release
    echo   create_release.bat 1.0.0 rc       # Release candidate
    echo.
    exit /b 1
)

set VERSION=%~1
set RELEASE_TYPE=%~2
if "%RELEASE_TYPE%"=="" set RELEASE_TYPE=stable

REM Determine tag name based on release type
if "%RELEASE_TYPE%"=="stable" (
    set TAG=v%VERSION%
) else if "%RELEASE_TYPE%"=="beta" (
    set TAG=v%VERSION%-beta.1
) else if "%RELEASE_TYPE%"=="rc" (
    set TAG=v%VERSION%-rc.1
) else if "%RELEASE_TYPE%"=="alpha" (
    set TAG=v%VERSION%-alpha.1
) else (
    echo Invalid release type: %RELEASE_TYPE%
    echo Valid types: stable, beta, rc, alpha
    exit /b 1
)

echo.
echo ================================
echo FarmVision Release Creator
echo ================================
echo.
echo Version: %VERSION%
echo Release Type: %RELEASE_TYPE%
echo Tag: %TAG%
echo.

REM Check for uncommitted changes
git status -s > nul 2>&1
if errorlevel 1 (
    echo Error: Git is not available or not a git repository
    exit /b 1
)

for /f %%i in ('git status -s') do (
    echo Error: You have uncommitted changes!
    git status -s
    echo.
    echo Please commit or stash your changes first.
    exit /b 1
)

REM Pull latest changes
echo Pulling latest changes...
git pull
if errorlevel 1 (
    echo Error: Failed to pull latest changes
    exit /b 1
)

REM Run tests if pytest is available
echo.
echo Running Tests...
where pytest >nul 2>nul
if %errorlevel%==0 (
    pytest
    if errorlevel 1 (
        echo Tests failed! Please fix before releasing.
        exit /b 1
    )
    echo Tests passed!
) else (
    echo pytest not found, skipping tests...
)

REM Update CHANGELOG.md
echo.
echo ================================
echo Update CHANGELOG.md
echo ================================
set /p CHANGELOG_UPDATED="Have you updated CHANGELOG.md? (y/n): "
if /i not "%CHANGELOG_UPDATED%"=="y" (
    echo Please update CHANGELOG.md and run this script again.
    exit /b 1
)

REM Create git tag
echo.
echo ================================
echo Creating Git Tag
echo ================================
echo Creating tag: %TAG%
echo.

set /p RELEASE_TITLE="Enter release title (or press enter for default): "
if "%RELEASE_TITLE%"=="" (
    if "%RELEASE_TYPE%"=="stable" set RELEASE_TITLE=Release v%VERSION%
    if "%RELEASE_TYPE%"=="beta" set RELEASE_TITLE=Beta Release v%VERSION%
    if "%RELEASE_TYPE%"=="rc" set RELEASE_TITLE=Release Candidate v%VERSION%
    if "%RELEASE_TYPE%"=="alpha" set RELEASE_TITLE=Alpha Release v%VERSION%
)

REM Create annotated tag
git tag -a "%TAG%" -m "%RELEASE_TITLE%"
if errorlevel 1 (
    echo Error: Failed to create tag
    exit /b 1
)

echo Tag created: %TAG%

REM Push tag to remote
echo.
echo ================================
echo Pushing to Remote
echo ================================
set /p PUSH_TAG="Push tag to GitHub? (y/n): "
if /i "%PUSH_TAG%"=="y" (
    git push origin "%TAG%"
    if errorlevel 1 (
        echo Error: Failed to push tag
        exit /b 1
    )
    echo Tag pushed to GitHub!
    echo.
    echo Next steps:
    echo 1. Go to: https://github.com/YOUR_USERNAME/farmvision/releases/new?tag=%TAG%
    echo 2. Add release notes from CHANGELOG.md
    echo 3. Upload any additional assets
    echo 4. Publish the release
    echo.
    echo Or use GitHub CLI:
    echo gh release create %TAG% --title "%RELEASE_TITLE%" --notes-file CHANGELOG.md
) else (
    echo Tag created locally but not pushed.
    echo To push later, run: git push origin %TAG%
)

echo.
echo ================================
echo Release Summary
echo ================================
echo Version: %VERSION%
echo Tag: %TAG%
echo Type: %RELEASE_TYPE%
echo.
echo Release creation completed!

endlocal
