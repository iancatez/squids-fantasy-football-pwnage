#!/usr/bin/env python3
"""
Build release distribution packages.

This script builds wheels and source distributions for GitHub releases.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Build distribution packages."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Building Release Distribution Packages")
    print("=" * 80)
    print()
    
    # Check if build is installed
    try:
        import build
    except ImportError:
        print("ERROR: 'build' package not installed.")
        print("Install it with: pip install build")
        sys.exit(1)
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print(f"Cleaning previous builds in {dist_dir}...")
        import shutil
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print(f"Cleaning previous builds in {build_dir}...")
        import shutil
        shutil.rmtree(build_dir)
    
    print()
    print("Building distribution packages...")
    print()
    
    # Build packages
    try:
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=project_root,
            check=True
        )
        
        print()
        print("=" * 80)
        print("Build Complete!")
        print("=" * 80)
        print()
        
        # List created files
        if dist_dir.exists():
            print("Created distribution files:")
            for file in sorted(dist_dir.glob("*")):
                size = file.stat().st_size / (1024 * 1024)  # Size in MB
                print(f"  - {file.name} ({size:.2f} MB)")
        
        print()
        print("Next steps:")
        print("1. Test installation: pip install dist/*.whl")
        print("2. Create git tag: git tag -a v0.1.0 -m 'Release v0.1.0'")
        print("3. Push tag: git push origin v0.1.0")
        print("4. Create GitHub release and attach files from dist/ folder")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

