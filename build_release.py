"""
Release build script for Abu Mukh Car Parts application.
Creates the final production version without console window.
"""
import os
import shutil
import subprocess
import sys
import time


def clean_build_dirs():
    """Clean build and dist directories"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            try:
                shutil.rmtree(dir_name)
            except Exception as e:
                print(f"Error cleaning {dir_name}: {e}")
                print("You may need to close any applications using these folders.")
                sys.exit(1)


def build_release_version():
    """Build the release version"""
    print("\nBuilding release version...")
    cmd = [sys.executable, "-m", "PyInstaller", "Abu Mukh Car Parts.spec", "--clean"]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Print output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Get the return code
    return_code = process.poll()

    if return_code == 0:
        print("\n✅ Release build successful!")
        print(f"Your executable is in: {os.path.abspath('dist/AbuMukhCarParts')}")
        return True
    else:
        # Get all stderr output
        errors = process.stderr.read()
        print("\n❌ Release build failed with errors:")
        print(errors)

        # Write errors to log file
        with open('build_errors.log', 'w') as f:
            f.write(errors)

        print(f"Errors written to: {os.path.abspath('build_errors.log')}")
        print("\nTIP: Run build_debug.py first to identify and fix any issues.")
        return False


def create_zip_package():
    """Create a ZIP package of the dist folder"""
    try:
        dist_path = os.path.abspath('dist/AbuMukhCarParts')
        if not os.path.exists(dist_path):
            print("Dist folder not found. Skipping ZIP creation.")
            return False

        import zipfile
        from datetime import datetime

        # Create zip filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"AbuMukhCarParts_{timestamp}.zip"

        print(f"\nCreating distribution package: {zip_filename}")

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(dist_path))
                    print(f"Adding: {arcname}")
                    zipf.write(file_path, arcname)

        zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # Size in MB
        print(f"\n✅ Package created: {os.path.abspath(zip_filename)} ({zip_size:.2f} MB)")
        return True

    except Exception as e:
        print(f"Error creating ZIP package: {e}")
        return False


def final_message(success):
    """Display final message with instructions"""
    if success:
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETE - DISTRIBUTION INSTRUCTIONS")
        print("=" * 60)
        print("To distribute your application:")
        print(f"1. The complete application is in: {os.path.abspath('dist/AbuMukhCarParts')}")
        print("2. You MUST distribute the ENTIRE FOLDER, not just the .exe file")
        print("3. The end user can run 'Abu Mukh Car Parts.exe' inside this folder")
        print("\nOptional ZIP package:")
        print("- A ZIP file was created in the current directory for easy distribution")
        print("- Users can extract this ZIP and run the application directly")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED - TROUBLESHOOTING STEPS")
        print("=" * 60)
        print("1. Run build_debug.py to create a debug version with console output")
        print("2. Check the error messages in the console window")
        print("3. Fix any issues identified in the error messages")
        print("4. Try building again")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("Abu Mukh Car Parts - RELEASE BUILD")
    print("=" * 60)
    print("This will create the final distribution version")
    print("=" * 60)

    # Confirm before proceeding
    response = input("Have you tested the debug version first? (y/n): ").lower()
    if response != 'y' and response != 'yes':
        print("\nIt's recommended to build and test the debug version first.")
        print("Run build_debug.py, test the application, then run this script.")
        sys.exit(0)

    # Clean previous build files
    clean_build_dirs()

    # Build release version
    start_time = time.time()
    success = build_release_version()

    if success:
        # Create ZIP package
        create_zip_package()

        # Show build time
        build_time = time.time() - start_time
        print(f"\nBuild completed in {build_time:.2f} seconds")

    # Show final message
    final_message(success)