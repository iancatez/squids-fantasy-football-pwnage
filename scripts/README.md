# Release Scripts

Helper scripts for building and releasing the package.

## build_release.py

Builds distribution packages (wheels and source distributions) for GitHub releases.

### Usage

```bash
# Install build tool first
pip install build

# Run the build script
python scripts/build_release.py
```

This will:
1. Clean previous builds
2. Build wheel (.whl) and source distribution (.tar.gz)
3. Create files in `dist/` folder
4. Show next steps for creating a GitHub release

### Manual Build

You can also build manually:

```bash
python -m build
```

This creates:
- `dist/pwn_fantasy_football-0.1.0-py3-none-any.whl` (wheel)
- `dist/pwn-fantasy-football-0.1.0.tar.gz` (source distribution)

## Release Process

See [RELEASE_PROCESS.md](../RELEASE_PROCESS.md) for complete release instructions.

