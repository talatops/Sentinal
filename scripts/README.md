# Team Contribution Simulation Script

This script generates realistic commit history for team members who haven't contributed yet. It creates separate branches for each member, makes mixed commits (realistic changes + empty commits), and optionally pushes to remote.

## Features

- **Dynamic path handling**: Works from any directory within the repo
- **Safety first**: Dry-run mode, confirmation prompts, backup branches
- **Realistic commits**: Mix of documentation, comments, formatting
- **Flexible**: Configurable members, commit counts, branch names
- **Non-destructive**: Creates separate branches, doesn't modify develop directly
- **Git-aware**: Detects existing contributors, handles git config properly

## Prerequisites

- Python 3.7+
- Git (must be installed and in PATH)
- Standard library only (no external packages needed)

## Usage

### Basic Usage

```bash
# Run with default settings (3 members, 3 commits each)
python scripts/simulate_contributions.py

# Or make it executable and run directly
chmod +x scripts/simulate_contributions.py
./scripts/simulate_contributions.py
```

### Custom Members

```bash
# Specify custom member names
python scripts/simulate_contributions.py --members alice bob charlie

# Specify number of commits per member
python scripts/simulate_contributions.py --members alice bob --commits-per-member 5
```

### Different Base Branch

```bash
# Branch from main instead of develop
python scripts/simulate_contributions.py --base-branch main
```

### Dry Run Mode

```bash
# See what would be done without making changes
python scripts/simulate_contributions.py --dry-run
```

### Auto-Push

```bash
# Automatically push all branches without asking
python scripts/simulate_contributions.py --push

# Combine with dry-run to see what would be pushed
python scripts/simulate_contributions.py --push --dry-run
```

### Member Configuration File

Create a JSON file with member details:

```json
{
  "alice": {
    "email": "alice@example.com"
  },
  "bob": {
    "email": "bob@example.com"
  }
}
```

Then use it:

```bash
python scripts/simulate_contributions.py --config scripts/member_config.json --members alice bob
```

## How It Works

1. **Detects Repository**: Automatically finds the git repository root from any directory
2. **Checks Existing Contributors**: Skips members who already have commits
3. **Creates Branches**: Creates separate branches like `contributions/member1-docs`
4. **Makes Commits**: 
   - 70% realistic commits (documentation updates, code comments, formatting)
   - 30% empty commits (for chore/documentation updates)
5. **Sets Git User**: Temporarily configures git user.name and user.email for each member
6. **Pushes Branches**: Optionally pushes to remote (asks by default)

## Example Output

```
Detected repository: /home/user/sentinal
Existing contributors: current_user
Base branch: develop
Members to process: member1, member2
Commits per member: 3

============================================================
Processing: member1
============================================================
  ✓ Created branch: contributions/member1-docs
    ✓ Commit 1: docs: update README with additional setup instructions
    ✓ Commit 2: chore: add code comments for better readability (empty)
    ✓ Commit 3: style: fix formatting in config.py
  Push branch 'contributions/member1-docs' to remote? [y/N]: y
  ✓ Pushed to origin/contributions/member1-docs

============================================================
Processing: member2
============================================================
  ✓ Created branch: contributions/member2-fixes
    ✓ Commit 1: docs: improve documentation in API
    ✓ Commit 2: chore: update .gitignore patterns
    ✓ Commit 3: style: fix formatting in Layout.jsx
  Push branch 'contributions/member2-fixes' to remote? [y/N]: n
  ⊘ Skipped pushing contributions/member2-fixes

============================================================
Summary:
  - Created 2 branches
  - Made 6 commits total
  - Returned to branch: develop
============================================================
```

## Safety Features

- **Clean Working Directory Check**: Warns if there are uncommitted changes
- **Dry Run Mode**: Test the script without making any changes
- **Confirmation Prompts**: Asks before pushing each branch (unless `--push` flag)
- **Original Branch Restoration**: Returns to your original branch after completion
- **Git Config Restoration**: Restores your original git user.name and user.email

## Commit Types

The script generates realistic commit messages in these categories:

- **docs**: Documentation updates, README changes, code comments
- **chore**: Maintenance tasks, dependency updates, code cleanup
- **style**: Formatting fixes, indentation, whitespace
- **refactor**: Code structure improvements (less common)

## Merging Branches

After the script creates branches, you can merge them back to develop:

```bash
# Checkout develop
git checkout develop

# Merge a member's branch
git merge contributions/member1-docs

# Or merge all at once
git merge contributions/member1-docs contributions/member2-fixes contributions/member3-improvements
```

## Troubleshooting

### "Not in a git repository"
Make sure you're running the script from within the git repository, or that git is properly installed.

### "Working directory is not clean"
Commit or stash your changes before running the script, or use `--dry-run` to test first.

### "Error creating branch"
Make sure the base branch exists and you have fetched the latest changes:
```bash
git fetch origin develop
```

### "Error pushing branch"
Check that you have push permissions to the remote repository and that the branch doesn't already exist remotely.

## Notes

- The script automatically skips members who already have commits in the repository
- Empty commits are used for realistic chore/documentation updates that don't require file changes
- File modifications are minimal and safe (adding comments, updating documentation)
- The script preserves your original git configuration and branch

## License

This script is part of Project Sentinel and follows the same license as the main project.

