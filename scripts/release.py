#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Release Script for Nyarc VRCat Tools
Handles version bumping, changelog generation, and release tagging
"""

import os
import re
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def get_script_dir():
    """Get the directory containing this script"""
    return Path(__file__).parent.absolute()

def get_project_root():
    """Get the project root directory"""
    return get_script_dir().parent

def run_git_command(cmd, capture_output=True):
    """Run a git command and return the output"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=get_project_root())
            if result.returncode != 0:
                print(f"Git command failed: {cmd}")
                print(f"Error: {result.stderr}")
                return None
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, cwd=get_project_root())
            return result.returncode == 0
    except Exception as e:
        print(f"Error running git command '{cmd}': {e}")
        return None

def get_current_version():
    """Extract current version from __init__.py"""
    init_file = get_project_root() / "nyarc_vrcat_tools" / "__init__.py"
    
    if not init_file.exists():
        print(f"Error: {init_file} not found")
        return None
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for version tuple in bl_info
    version_match = re.search(r'"version":\s*\(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)', content)
    if not version_match:
        print("Error: Could not find version in __init__.py")
        return None
    
    return tuple(map(int, version_match.groups()))

def get_latest_release_version():
    """Get the latest release version from git tags"""
    # Get all tags sorted by version
    tags_output = run_git_command("git tag -l 'v*' --sort=-version:refname")
    
    if not tags_output:
        print("No existing tags found - this will be the first release")
        return (0, 0, 0)
    
    latest_tag = tags_output.split('\n')[0] if tags_output else None
    if not latest_tag:
        return (0, 0, 0)
    
    # Extract version from tag (e.g., v0.0.1 -> 0.0.1)
    version_match = re.search(r'v(\d+)\.(\d+)\.(\d+)', latest_tag)
    if not version_match:
        print(f"Warning: Could not parse version from tag {latest_tag}")
        return (0, 0, 0)
    
    return tuple(map(int, version_match.groups()))

def bump_version(current_version, bump_type):
    """Calculate new version based on bump type"""
    major, minor, patch = current_version
    
    if bump_type == "major":
        return (major + 1, 0, 0)
    elif bump_type == "minor":
        return (major, minor + 1, 0)
    elif bump_type == "patch":
        return (major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

def update_version_files(new_version):
    """Update version in __init__.py and blender_manifest.toml"""
    major, minor, patch = new_version
    version_str = f"{major}.{minor}.{patch}"
    version_tuple = f"({major}, {minor}, {patch})"
    
    # Update __init__.py
    init_file = get_project_root() / "nyarc_vrcat_tools" / "__init__.py"
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version tuple
    content = re.sub(
        r'"version":\s*\(\s*\d+,\s*\d+,\s*\d+\s*\)',
        f'"version": {version_tuple}',
        content
    )
    
    # Update UI display version
    content = re.sub(
        r'header_row\.label\(text="Nyarc VRCat Tools v[\d.]+",',
        f'header_row.label(text="Nyarc VRCat Tools v{version_str}",',
        content
    )
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update blender_manifest.toml
    manifest_file = get_project_root() / "blender_manifest.toml"
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(
            r'version = "[\d.]+"',
            f'version = "{version_str}"',
            content,
            count=1  # Only replace the first occurrence (not schema_version)
        )
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return version_str

def generate_changelog(latest_release_version):
    """Generate changelog from git commits since last release"""
    if latest_release_version == (0, 0, 0):
        # First release - get all commits
        git_log = run_git_command("git log --oneline --reverse")
    else:
        # Get commits since last release
        latest_tag = f"v{latest_release_version[0]}.{latest_release_version[1]}.{latest_release_version[2]}"
        git_log = run_git_command(f"git log {latest_tag}..HEAD --oneline")
    
    if not git_log:
        return "* Initial release"
    
    commits = git_log.split('\n')
    changelog_entries = []
    
    # Categorize commits
    features = []
    fixes = []
    other = []
    
    for commit in commits:
        if not commit.strip():
            continue
            
        # Extract commit message (everything after the hash)
        parts = commit.split(' ', 1)
        if len(parts) < 2:
            continue
            
        message = parts[1].strip()
        
        # Categorize based on conventional commit format or keywords
        if (message.lower().startswith('feat:') or 
            message.lower().startswith('feature:') or
            'add' in message.lower() or
            'implement' in message.lower() or
            'new' in message.lower()):
            features.append(f"* {message}")
        elif (message.lower().startswith('fix:') or
              message.lower().startswith('bug:') or
              'fix' in message.lower() or
              'resolve' in message.lower() or
              'correct' in message.lower()):
            fixes.append(f"* {message}")
        else:
            other.append(f"* {message}")
    
    # Build changelog
    changelog = []
    
    if features:
        changelog.append("### New Features")
        changelog.extend(features)
        changelog.append("")
    
    if fixes:
        changelog.append("### Bug Fixes")
        changelog.extend(fixes)
        changelog.append("")
    
    if other:
        changelog.append("### Other Changes")
        changelog.extend(other)
        changelog.append("")
    
    return "\n".join(changelog) if changelog else "* Initial release"

def update_changelog_file(new_version, changelog_content):
    """Update CHANGELOG.md with new version entry"""
    version_str = f"{new_version[0]}.{new_version[1]}.{new_version[2]}"
    changelog_file = get_project_root() / "CHANGELOG.md"
    
    # Create new version entry
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"## v{version_str} ({today})\n\n{changelog_content}\n\n"
    
    if changelog_file.exists():
        with open(changelog_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Insert new entry after the first heading
        if existing_content.startswith('# '):
            lines = existing_content.split('\n')
            header_end = 1
            while header_end < len(lines) and not lines[header_end].startswith('## '):
                header_end += 1
            
            new_content = '\n'.join(lines[:header_end]) + '\n\n' + new_entry + '\n'.join(lines[header_end:])
        else:
            new_content = new_entry + existing_content
    else:
        # Create new changelog file
        new_content = f"# Changelog\n\nAll notable changes to Nyarc VRCat Tools will be documented in this file.\n\n{new_entry}"
    
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

def create_release_commit_and_tag(new_version, changelog_content):
    """Create release commit and tag"""
    version_str = f"{new_version[0]}.{new_version[1]}.{new_version[2]}"
    
    # Add changed files
    if not run_git_command("git add nyarc_vrcat_tools/__init__.py blender_manifest.toml CHANGELOG.md", False):
        print("Error: Failed to stage files")
        return False
    
    # Create release commit
    commit_message = f"release: v{version_str}\n\n{changelog_content}"
    if not run_git_command(f'git commit -m "{commit_message}"', False):
        print("Error: Failed to create release commit")
        return False
    
    # Create tag
    tag_message = f"Release v{version_str}"
    if not run_git_command(f'git tag -a v{version_str} -m "{tag_message}"', False):
        print("Error: Failed to create tag")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Automated release script for Nyarc VRCat Tools")
    parser.add_argument("bump_type", choices=["major", "minor", "patch"], 
                       help="Type of version bump")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    # Get current version from git tags (not from files)
    print("[INFO] Checking latest release version...")
    latest_release = get_latest_release_version()
    current_file_version = get_current_version()
    
    if current_file_version is None:
        sys.exit(1)
    
    print(f"Latest release: v{latest_release[0]}.{latest_release[1]}.{latest_release[2]}")
    print(f"Current file version: v{current_file_version[0]}.{current_file_version[1]}.{current_file_version[2]}")
    
    # Calculate new version based on LATEST RELEASE, not current file version
    new_version = bump_version(latest_release, args.bump_type)
    version_str = f"{new_version[0]}.{new_version[1]}.{new_version[2]}"
    
    print(f"[RELEASE] Preparing release v{version_str}")
    
    # Generate changelog
    print("[CHANGELOG] Generating changelog...")
    changelog_content = generate_changelog(latest_release)
    
    print(f"\nChangelog for v{version_str}:")
    print("-" * 40)
    print(changelog_content)
    print("-" * 40)
    
    if args.dry_run:
        print("\n[DRY RUN] Would update:")
        print(f"  - nyarc_vrcat_tools/__init__.py: version = {new_version}")
        print(f"  - blender_manifest.toml: version = \"{version_str}\"")
        print(f"  - CHANGELOG.md: Add v{version_str} entry")
        print(f"  - Git commit: release: v{version_str}")
        print(f"  - Git tag: v{version_str}")
        print(f"\nTo complete the release, run:")
        print(f"  git push origin main v{version_str}")
        return
    
    # Update version files
    print("[FILES] Updating version files...")
    update_version_files(new_version)
    
    # Update changelog
    print("[CHANGELOG] Updating CHANGELOG.md...")
    update_changelog_file(new_version, changelog_content)
    
    # Create commit and tag
    print("[GIT] Creating release commit and tag...")
    if not create_release_commit_and_tag(new_version, changelog_content):
        print("[ERROR] Failed to create release commit and tag")
        sys.exit(1)
    
    print(f"[SUCCESS] Release v{version_str} prepared successfully!")
    print(f"\n[NEXT] To publish the release, run:")
    print(f"  git push origin main v{version_str}")
    print(f"\n[GITHUB] GitHub Actions will automatically:")
    print(f"  - Build the addon ZIP file")
    print(f"  - Create GitHub release with downloads")
    print(f"  - Attach nyarc-vrcat-tools-v{version_str}.zip")

if __name__ == "__main__":
    main()