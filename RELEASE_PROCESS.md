# Release Process Guide

This guide explains how to create and publish a release for this project.

## Overview

For Python packages, you have several options for distribution:

1. **Source Code Only** (Simplest) - Users install directly from GitHub
2. **Distribution Packages** (Recommended) - Build wheels and source distributions
3. **Standalone Executables** (Optional) - Create .exe/.app files (usually not needed)

## Option 1: Source Code Release (Simplest)

This is the easiest approach - just tag and release the source code.

### Steps:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.0"
   ```

2. **Create a git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

3. **Create GitHub Release**:
   - Go to GitHub → Releases → "Draft a new release"
   - Choose tag: `v0.1.0`
   - Title: `v0.1.0 - Initial Release`
   - Description: Copy from `RELEASE.md`
   - Attach `RELEASE.md` as a file (optional)
   - Publish release

4. **Users install via**:
   ```bash
   pip install git+https://github.com/yourusername/squids-fantasy-football-pwnage.git@v0.1.0
   # Or clone and install
   git clone https://github.com/yourusername/squids-fantasy-football-pwnage.git
   cd squids-fantasy-football-pwnage
   git checkout v0.1.0
   pip install -e .
   ```

## Option 2: Distribution Packages (Recommended)

Build wheels and source distributions for easier installation.

### Prerequisites:

```bash
pip install build twine
```

### Steps:

1. **Update version** in `pyproject.toml`

2. **Build distribution packages**:
   ```bash
   python -m build
   ```
   
   This creates:
   - `dist/pwn_fantasy_football-0.1.0-py3-none-any.whl` (wheel)
   - `dist/pwn-fantasy-football-0.1.0.tar.gz` (source distribution)

3. **Test the build** (optional):
   ```bash
   pip install dist/pwn_fantasy_football-0.1.0-py3-none-any.whl
   ```

4. **Create git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

5. **Create GitHub Release**:
   - Go to GitHub → Releases → "Draft a new release"
   - Choose tag: `v0.1.0`
   - Title: `v0.1.0 - Initial Release`
   - Description: Copy from `RELEASE.md`
   - **Attach files**: Upload both files from `dist/` folder:
     - `pwn_fantasy_football-0.1.0-py3-none-any.whl`
     - `pwn-fantasy-football-0.1.0.tar.gz`
   - Publish release

6. **Users install via**:
   ```bash
   # Download wheel from GitHub release, then:
   pip install pwn_fantasy_football-0.1.0-py3-none-any.whl
   
   # Or from source:
   pip install pwn-fantasy-football-0.1.0.tar.gz
   ```

### Optional: Publish to PyPI

If you want to publish to PyPI (Python Package Index):

1. **Create PyPI account**: https://pypi.org/account/register/

2. **Test on TestPyPI first**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

3. **Publish to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

4. **Users install via**:
   ```bash
   pip install pwn-fantasy-football
   ```

## Option 3: Standalone Executables (Advanced)

Only needed if you want users to run without Python installed.

### Using PyInstaller:

```bash
pip install pyinstaller

# Create executable
pyinstaller --onefile --name fantasy-predict src/pwn_fantasy_football/cli.py
```

**Note**: This is usually unnecessary for Python packages and creates large files.

## Recommended Approach

For this project, **Option 2 (Distribution Packages)** is recommended because:

- ✅ Easy installation for users
- ✅ Works across platforms
- ✅ Standard Python distribution method
- ✅ Can optionally publish to PyPI later
- ✅ No need for binaries

## Quick Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `RELEASE.md` with release notes
- [ ] Run tests: `pytest`
- [ ] Build packages: `python -m build`
- [ ] Test installation: `pip install dist/*.whl`
- [ ] Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Create GitHub release with distribution files
- [ ] (Optional) Publish to PyPI

## GitHub Release Template

**Title**: `v0.1.0 - Initial Release`

**Description**:
```markdown
## v0.1.0 - Initial Release

See [RELEASE.md](RELEASE.md) for complete release notes.

### Installation

Download the wheel file below and install:
```bash
pip install pwn_fantasy_football-0.1.0-py3-none-any.whl
```

Or install from source:
```bash
pip install git+https://github.com/yourusername/squids-fantasy-football-pwnage.git@v0.1.0
```

### What's New

- Data fetching module with comprehensive NFL data collection
- Statistical prediction algorithm
- Unified CMDlet-style interface
- Command-line interfaces (Python, PowerShell, Batch)
- Comprehensive test suite
- Full documentation suite
```

**Attachments**:
- `pwn_fantasy_football-0.1.0-py3-none-any.whl`
- `pwn-fantasy-football-0.1.0.tar.gz`
- `RELEASE.md` (optional)

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 0.1.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Next Steps After Release

1. Update `pyproject.toml` version to next development version (e.g., 0.1.1-dev)
2. Create a new branch for next release
3. Continue development
4. Update `RELEASE.md` for next release

---

**Note**: You don't need to create a binary (.exe) for a Python package. Distribution packages (wheels) are the standard and recommended approach.

