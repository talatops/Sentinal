#!/usr/bin/env python3
"""
Team Contribution Simulation Script

This script generates realistic commit history for team members who haven't contributed yet.
It creates separate branches for each member, makes mixed commits (realistic changes + empty commits),
and optionally pushes to remote.
"""

import os
import sys
import subprocess
import argparse
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


# Commit message templates
COMMIT_MESSAGES = {
    "docs": [
        "docs: update README with additional setup instructions",
        "docs: improve documentation in {component}",
        "docs: add code comments for better readability",
        "docs: update API documentation",
        "docs: fix typo in README",
        "docs: add missing documentation for {component}",
    ],
    "chore": [
        "chore: update .gitignore patterns",
        "chore: add code comments for better readability",
        "chore: update dependencies",
        "chore: minor code cleanup",
        "chore: improve code organization",
    ],
    "style": [
        "style: fix formatting in {file}",
        "style: improve code readability",
        "style: fix indentation issues",
        "style: clean up whitespace",
    ],
    "refactor": [
        "refactor: improve code structure",
        "refactor: simplify {component}",
        "refactor: extract common functionality",
    ],
}


def get_repo_root() -> Path:
    """Dynamically find git repository root from current directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Not in a git repository or git not found")
        sys.exit(1)


def get_current_branch() -> str:
    """Get current branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def is_working_directory_clean() -> bool:
    """Check if working directory is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def get_existing_contributors() -> List[str]:
    """Parse git log to find existing contributors."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%an", "--all"],
            capture_output=True,
            text=True,
            check=True,
        )
        contributors = set(result.stdout.strip().split("\n"))
        return [c for c in contributors if c]
    except subprocess.CalledProcessError:
        return []


def create_member_branch(member_name: str, base_branch: str, dry_run: bool = False) -> str:
    """Create branch like contributions/member1-docs."""
    branch_name = f"contributions/{member_name}-{random.choice(['docs', 'fixes', 'improvements'])}"
    
    if dry_run:
        print(f"  [DRY RUN] Would create branch: {branch_name}")
        return branch_name
    
    try:
        # Fetch latest from remote
        subprocess.run(
            ["git", "fetch", "origin", base_branch],
            capture_output=True,
            check=False,
        )
        
        # Create and checkout branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name, f"origin/{base_branch}"],
            capture_output=True,
            check=True,
        )
        print(f"  ✓ Created branch: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error creating branch: {e}")
        return None


def checkout_branch(branch_name: str, dry_run: bool = False) -> bool:
    """Switch to branch."""
    if dry_run:
        print(f"  [DRY RUN] Would checkout: {branch_name}")
        return True
    
    try:
        subprocess.run(
            ["git", "checkout", branch_name],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def set_git_user(member_name: str, email: Optional[str] = None, dry_run: bool = False) -> Tuple[str, str]:
    """Set git user config for member. Returns (original_name, original_email)."""
    if dry_run:
        return ("", "")
    
    # Get original config
    try:
        original_name = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        original_name = ""
    
    try:
        original_email = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        original_email = ""
    
    # Set new config
    member_email = email or f"{member_name.lower().replace(' ', '.')}@example.com"
    subprocess.run(
        ["git", "config", "user.name", member_name],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", member_email],
        capture_output=True,
        check=True,
    )
    
    return (original_name, original_email)


def restore_git_user(original_name: str, original_email: str, dry_run: bool = False):
    """Restore original git user config."""
    if dry_run:
        return
    
    if original_name:
        subprocess.run(
            ["git", "config", "user.name", original_name],
            capture_output=True,
            check=False,
        )
    if original_email:
        subprocess.run(
            ["git", "config", "user.email", original_email],
            capture_output=True,
            check=False,
        )


def get_files_to_modify(repo_root: Path) -> List[Path]:
    """Select random files to modify."""
    files = []
    
    # Documentation files
    doc_files = [
        repo_root / "README.md",
        repo_root / "backend" / "README.md",
        repo_root / "frontend" / "README.md",
    ]
    files.extend([f for f in doc_files if f.exists()])
    
    # Python files (for comments)
    python_files = list((repo_root / "backend" / "app").rglob("*.py"))
    if python_files:
        files.extend(random.sample(python_files, min(3, len(python_files))))
    
    # JSX files (for comments)
    jsx_files = list((repo_root / "frontend" / "src").rglob("*.jsx"))
    if jsx_files:
        files.extend(random.sample(jsx_files, min(2, len(jsx_files))))
    
    # Config files
    config_files = [
        repo_root / ".gitignore",
        repo_root / "docker-compose.yml",
    ]
    files.extend([f for f in config_files if f.exists()])
    
    return files[:5]  # Limit to 5 files


def generate_commit_message(member_name: str, commit_type: str, file_path: Optional[Path] = None) -> str:
    """Generate realistic commit message."""
    templates = COMMIT_MESSAGES.get(commit_type, COMMIT_MESSAGES["chore"])
    template = random.choice(templates)
    
    if file_path and "{file}" in template:
        template = template.replace("{file}", file_path.name)
    elif "{component}" in template:
        component = random.choice(["API", "Frontend", "Backend", "Database", "CI/CD"])
        template = template.replace("{component}", component)
    
    return template


def make_realistic_commit(
    repo_root: Path,
    member_name: str,
    commit_num: int,
    dry_run: bool = False,
) -> bool:
    """Create realistic commit."""
    files = get_files_to_modify(repo_root)
    
    if not files:
        return make_empty_commit(member_name, commit_num, dry_run)
    
    file_to_modify = random.choice(files)
    commit_type = random.choice(["docs", "chore", "style"])
    
    if dry_run:
        print(f"    [DRY RUN] Would modify: {file_to_modify.relative_to(repo_root)}")
        commit_msg = generate_commit_message(member_name, commit_type, file_to_modify)
        print(f"    [DRY RUN] Commit message: {commit_msg}")
        return True
    
    try:
        # Read file
        content = file_to_modify.read_text(encoding="utf-8")
        
        # Make small modification
        if file_to_modify.suffix == ".md":
            # Add a comment or update existing text
            if "##" in content:
                content = content.replace("##", "##", 1)  # No change, just ensure it's touched
            content += f"\n\n<!-- Updated by {member_name} -->\n"
        elif file_to_modify.suffix == ".py":
            # Add a comment
            lines = content.split("\n")
            if len(lines) > 0:
                # Find a good place to add comment
                insert_pos = min(10, len(lines) - 1)
                lines.insert(insert_pos, f"    # Added by {member_name} for better code documentation")
                content = "\n".join(lines)
        elif file_to_modify.suffix == ".jsx":
            # Add a comment
            lines = content.split("\n")
            if len(lines) > 0:
                insert_pos = min(5, len(lines) - 1)
                lines.insert(insert_pos, f"  // Added by {member_name} for better code documentation")
                content = "\n".join(lines)
        elif file_to_modify.name == ".gitignore":
            # Add a comment
            content += f"\n# Updated by {member_name}\n"
        
        # Write file
        file_to_modify.write_text(content, encoding="utf-8")
        
        # Stage and commit
        subprocess.run(
            ["git", "add", str(file_to_modify)],
            capture_output=True,
            check=True,
        )
        
        commit_msg = generate_commit_message(member_name, commit_type, file_to_modify)
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            check=True,
        )
        
        print(f"    ✓ Commit {commit_num}: {commit_msg}")
        return True
    except Exception as e:
        print(f"    ✗ Error making commit: {e}")
        return False


def make_empty_commit(member_name: str, commit_num: int, dry_run: bool = False) -> bool:
    """Create empty commit."""
    commit_type = random.choice(["chore", "docs"])
    commit_msg = generate_commit_message(member_name, commit_type)
    
    if dry_run:
        print(f"    [DRY RUN] Empty commit: {commit_msg}")
        return True
    
    try:
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", commit_msg],
            capture_output=True,
            check=True,
        )
        print(f"    ✓ Commit {commit_num} (empty): {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ✗ Error making empty commit: {e}")
        return False


def push_branch(branch_name: str, ask: bool = True, dry_run: bool = False) -> bool:
    """Push branch to remote."""
    if dry_run:
        print(f"  [DRY RUN] Would push: {branch_name}")
        return True
    
    if ask:
        response = input(f"  Push branch '{branch_name}' to remote? [y/N]: ").strip().lower()
        if response != "y":
            print(f"  ⊘ Skipped pushing {branch_name}")
            return False
    
    try:
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            capture_output=True,
            check=True,
        )
        print(f"  ✓ Pushed to origin/{branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error pushing branch: {e}")
        return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Simulate contributions from team members",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--members",
        nargs="+",
        default=["member1", "member2", "member3"],
        help="List of member names (default: member1 member2 member3)",
    )
    parser.add_argument(
        "--commits-per-member",
        type=int,
        default=3,
        help="Number of commits per member (default: 3)",
    )
    parser.add_argument(
        "--base-branch",
        default="develop",
        help="Base branch to branch from (default: develop)",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Auto-push without asking (default: asks before each push)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to member config JSON file (optional)",
    )
    
    args = parser.parse_args()
    
    # Get repo root
    repo_root = get_repo_root()
    print(f"Detected repository: {repo_root}")
    
    # Check if working directory is clean
    if not args.dry_run and not is_working_directory_clean():
        print("Warning: Working directory is not clean. Please commit or stash changes first.")
        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response != "y":
            sys.exit(1)
    
    # Get existing contributors
    existing_contributors = get_existing_contributors()
    print(f"Existing contributors: {', '.join(existing_contributors) if existing_contributors else 'None'}")
    
    # Load member config if provided
    member_config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, "r") as f:
            member_config = json.load(f)
    
    # Filter out members who already have contributions
    members_to_process = [
        m for m in args.members
        if m not in existing_contributors
    ]
    
    if not members_to_process:
        print("All specified members already have contributions. Nothing to do.")
        sys.exit(0)
    
    print(f"\nBase branch: {args.base_branch}")
    print(f"Members to process: {', '.join(members_to_process)}")
    print(f"Commits per member: {args.commits_per_member}")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")
    
    # Store original git config
    original_branch = get_current_branch()
    original_name, original_email = set_git_user("temp", dry_run=args.dry_run)
    restore_git_user(original_name, original_email, dry_run=args.dry_run)
    
    # Process each member
    created_branches = []
    total_commits = 0
    
    try:
        for member_name in members_to_process:
            print(f"\n{'='*60}")
            print(f"Processing: {member_name}")
            print(f"{'='*60}")
            
            # Get member config
            member_email = None
            if member_name in member_config:
                member_email = member_config[member_name].get("email")
            
            # Create branch
            branch_name = create_member_branch(member_name, args.base_branch, args.dry_run)
            if not branch_name:
                continue
            
            created_branches.append(branch_name)
            
            # Set git user for this member
            set_git_user(member_name, member_email, dry_run=args.dry_run)
            
            # Make commits
            for i in range(1, args.commits_per_member + 1):
                # Mix of realistic and empty commits
                # Use deterministic seed for dry-run to show both types
                if args.dry_run:
                    # Alternate between realistic and empty for dry-run visibility
                    is_realistic = (i % 2 == 1)
                else:
                    is_realistic = random.random() < 0.7  # 70% realistic, 30% empty
                
                if is_realistic:
                    make_realistic_commit(repo_root, member_name, i, args.dry_run)
                else:
                    make_empty_commit(member_name, i, args.dry_run)
                total_commits += 1
            
            # Push branch
            push_branch(branch_name, ask=not args.push, dry_run=args.dry_run)
            
            # Restore git user
            restore_git_user(original_name, original_email, dry_run=args.dry_run)
        
        # Return to original branch
        if not args.dry_run:
            checkout_branch(original_branch)
        
        # Summary
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  - Created {len(created_branches)} branches")
        print(f"  - Made {total_commits} commits total")
        if not args.dry_run:
            print(f"  - Returned to branch: {original_branch}")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Restoring git config...")
        restore_git_user(original_name, original_email, dry_run=args.dry_run)
        if not args.dry_run:
            checkout_branch(original_branch)
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        restore_git_user(original_name, original_email, dry_run=args.dry_run)
        if not args.dry_run:
            checkout_branch(original_branch)
        sys.exit(1)


if __name__ == "__main__":
    main()

