"""
Cleanup script to fix permission issues and rebuild.
This script will:
1. Close any running processes that might lock build files
2. Clean build and dist directories
3. Build the application with the correct spec file
"""
import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 70)
    print(message)
    print("=" * 70)

def close_processes():
    """Attempt to close processes that might be locking files"""
    print_header("CLOSING PROCESSES")

    # On Windows, we need to use taskkill to force close processes
    if sys.platform == 'win32':
        try:
            # Try to close any python processes that might be locking files
            print("Attempting to close Python processes...")
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Try to close the application if it's running
            print("Attempting to close application processes...")
            subprocess.run(["taskkill", "/F", "/IM", "Abu Mukh Car Parts.exe"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Close any PyInstaller processes
            print("Attempting to close PyInstaller processes...")
            subprocess.run(["taskkill", "/F", "/IM", "PyInstaller.exe"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Allow time for processes to fully close
            print("Waiting for processes to close...")
            time.sleep(2)

        except Exception as e:
            print(f"Error closing processes: {e}")

    print("✅ Process cleanup completed")

def clean_build_directories():
    """Clean build and dist directories"""
    print_header("CLEANING BUILD DIRECTORIES")

    # Directories to clean
    dirs_to_clean = ['build', 'dist', '__pycache__']

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                print(f"Removing {dir_path}...")
                shutil.rmtree(dir_path, ignore_errors=True)
                # Double check if directory is gone
                if dir_path.exists():
                    print(f"Could not fully remove {dir_path}")
                else:
                    print(f"✅ Removed {dir_path}")
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")

    # Also clean PyInstaller cache
    try:
        import PyInstaller
        cache_dir = Path(PyInstaller.config.CONF['workpath'])
        if cache_dir.exists():
            print(f"Cleaning PyInstaller cache: {cache_dir}")
            shutil.rmtree(cache_dir, ignore_errors=True)
            print("✅ Cleaned PyInstaller cache")
    except Exception as e:
        print(f"Could not clean PyInstaller cache: {e}")

    print("✅ Directory cleanup completed")

def build_application():
    """Build the application using PyInstaller"""
    print_header("BUILDING APPLICATION")

    # Check if spec file exists
    spec_file = Path("Abu Mukh Car Parts.spec")
    if not spec_file.exists():
        print(f"❌ Spec file not found: {spec_file}")
        return False

    # Build command
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"]

    print(f"Running: {' '.join(cmd)}")
    print("This will take several minutes...")

    try:
        # Run PyInstaller with output displayed
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Show output in real-time
        for line in process.stdout:
            print(line.strip())

        # Wait for process to complete
        result = process.wait()

        if result == 0:
            print("\n✅ Build completed successfully!")
            return True
        else:
            print(f"\n❌ Build failed with exit code: {result}")
            return False

    except Exception as e:
        print(f"❌ Error running PyInstaller: {e}")
        return False

def verify_build():
    """Verify the build completed successfully"""
    print_header("VERIFYING BUILD")

    # Check for executable
    dist_dir = Path("dist") / "AbuMukhCarParts"
    exe_file = dist_dir / "Abu Mukh Car Parts.exe"

    if not dist_dir.exists():
        print(f"❌ Distribution directory not found: {dist_dir}")
        return False

    if not exe_file.exists():
        print(f"❌ Executable not found: {exe_file}")
        return False

    print(f"✅ Executable created: {exe_file}")

    # Check for resources directory
    resources_dir = dist_dir / "resources"
    if not resources_dir.exists():
        print(f"❌ Resources directory not found: {resources_dir}")
        return False

    print(f"✅ Resources directory found: {resources_dir}")

    # Check for Qt plugins
    qt_plugins_dir = dist_dir / "PyQt5" / "Qt5" / "plugins" / "imageformats"
    if not qt_plugins_dir.exists():
        print(f"❌ Qt image plugins not found: {qt_plugins_dir}")
        return False

    print(f"✅ Qt image plugins found: {qt_plugins_dir}")
    return True

if __name__ == "__main__":
    print_header("BUILD CLEANUP AND REBUILD UTILITY")
    print("This script will clean up your build environment and rebuild the application")

    # Ask for confirmation
    confirm = input("This will close applications and delete the build folder. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)

    # Run the cleanup and build process
    close_processes()
    clean_build_directories()

    if build_application():
        verify_build()

        print_header("BUILD COMPLETE")
        print("Your application should now display icons correctly!")
        print(f"The executable is in: {os.path.abspath('dist/AbuMukhCarParts')}")
    else:
        print_header("BUILD FAILED")
        print("Try these steps:")
        print("1. Close all applications and restart your computer")
        print("2. Run this script again")
        print("3. If it still fails, try building manually:")
        print("   python -m PyInstaller \"Abu Mukh Car Parts.spec\" --clean")