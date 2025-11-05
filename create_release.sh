#!/bin/bash

# FarmVision Release Script
# This script helps create a new release with proper tagging

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Print header
print_header() {
    echo ""
    print_message "$BLUE" "================================"
    print_message "$BLUE" "$1"
    print_message "$BLUE" "================================"
    echo ""
}

# Check if version is provided
if [ -z "$1" ]; then
    print_message "$RED" "Error: Version number required"
    echo "Usage: ./create_release.sh <version> [release-type]"
    echo ""
    echo "Examples:"
    echo "  ./create_release.sh 1.0.0          # Stable release"
    echo "  ./create_release.sh 1.0.0 beta     # Beta release"
    echo "  ./create_release.sh 1.0.0 rc       # Release candidate"
    echo ""
    exit 1
fi

VERSION=$1
RELEASE_TYPE=${2:-stable}

# Determine tag name based on release type
case $RELEASE_TYPE in
    stable)
        TAG="v$VERSION"
        ;;
    beta)
        TAG="v$VERSION-beta.1"
        ;;
    rc)
        TAG="v$VERSION-rc.1"
        ;;
    alpha)
        TAG="v$VERSION-alpha.1"
        ;;
    *)
        print_message "$RED" "Invalid release type: $RELEASE_TYPE"
        echo "Valid types: stable, beta, rc, alpha"
        exit 1
        ;;
esac

print_header "FarmVision Release Creator"

print_message "$BLUE" "Version: $VERSION"
print_message "$BLUE" "Release Type: $RELEASE_TYPE"
print_message "$BLUE" "Tag: $TAG"
echo ""

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    print_message "$YELLOW" "Warning: You are not on main/master branch!"
    print_message "$YELLOW" "Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    print_message "$RED" "Error: You have uncommitted changes!"
    git status -s
    echo ""
    print_message "$YELLOW" "Please commit or stash your changes first."
    exit 1
fi

# Pull latest changes
print_message "$GREEN" "Pulling latest changes..."
git pull origin $CURRENT_BRANCH

# Run tests
print_header "Running Tests"
print_message "$YELLOW" "Running pytest..."
if command -v pytest &> /dev/null; then
    pytest || {
        print_message "$RED" "Tests failed! Please fix before releasing."
        exit 1
    }
    print_message "$GREEN" "✓ Tests passed!"
else
    print_message "$YELLOW" "pytest not found, skipping tests..."
fi

# Run linters
print_header "Running Code Quality Checks"

if command -v flake8 &> /dev/null; then
    print_message "$YELLOW" "Running flake8..."
    flake8 . || print_message "$YELLOW" "Warning: flake8 found issues"
fi

if command -v black &> /dev/null; then
    print_message "$YELLOW" "Checking code formatting..."
    black --check . || print_message "$YELLOW" "Warning: Code formatting issues found"
fi

# Update CHANGELOG.md
print_header "Update CHANGELOG.md"
print_message "$YELLOW" "Please update CHANGELOG.md with release notes"
read -p "Have you updated CHANGELOG.md? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_message "$RED" "Please update CHANGELOG.md and run this script again."
    exit 1
fi

# Create git tag
print_header "Creating Git Tag"
print_message "$GREEN" "Creating tag: $TAG"

read -p "Enter release title (or press enter for default): " RELEASE_TITLE
if [ -z "$RELEASE_TITLE" ]; then
    case $RELEASE_TYPE in
        stable)
            RELEASE_TITLE="Release v$VERSION"
            ;;
        beta)
            RELEASE_TITLE="Beta Release v$VERSION"
            ;;
        rc)
            RELEASE_TITLE="Release Candidate v$VERSION"
            ;;
        alpha)
            RELEASE_TITLE="Alpha Release v$VERSION"
            ;;
    esac
fi

# Create annotated tag
git tag -a "$TAG" -m "$RELEASE_TITLE"

print_message "$GREEN" "✓ Tag created: $TAG"

# Push tag to remote
print_header "Pushing to Remote"
read -p "Push tag to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin "$TAG"
    print_message "$GREEN" "✓ Tag pushed to GitHub!"
    echo ""
    print_message "$BLUE" "Next steps:"
    echo "1. Go to: https://github.com/YOUR_USERNAME/farmvision/releases/new?tag=$TAG"
    echo "2. Add release notes from CHANGELOG.md"
    echo "3. Upload any additional assets"
    echo "4. Publish the release"
    echo ""
    print_message "$GREEN" "Or use GitHub CLI:"
    echo "gh release create $TAG --title '$RELEASE_TITLE' --notes-file CHANGELOG.md"
else
    print_message "$YELLOW" "Tag created locally but not pushed."
    print_message "$YELLOW" "To push later, run: git push origin $TAG"
fi

print_header "Release Summary"
print_message "$GREEN" "✓ Version: $VERSION"
print_message "$GREEN" "✓ Tag: $TAG"
print_message "$GREEN" "✓ Type: $RELEASE_TYPE"
echo ""
print_message "$BLUE" "Release creation completed!"
