import os
import subprocess
import sys
import time

# Clean previous build folders if they exist
for folder in ['build', 'dist']:
    if os.path.exists(folder):
        print(f"Removing {folder} folder...")
        import shutil
        shutil.rmtree(folder)

print("Starting PyInstaller build...")
print("This will take several minutes. You'll see updates every 10 seconds.")

# Start the PyInstaller process
cmd = [sys.executable, "-m", "PyInstaller", "--name", "Abu Mukh Car Parts",
       "--windowed", "--clean", "main.py",
       "--add-data", "resources/*;resources",
       "--add-data", "translations/*;translations"]

process = subprocess.Popen(cmd)

# Monitor progress by checking if build folders are growing
start_time = time.time()
last_check = start_time
build_exists = False
dist_exists = False

try:
    while process.poll() is None:  # While the process is still running
        current_time = time.time()

        # Show an update every 10 seconds
        if current_time - last_check >= 10:
            elapsed = current_time - start_time
            print(f"Still building... ({elapsed:.0f} seconds elapsed)")

            # Check if build and dist folders exist and report their size
            if os.path.exists('build') and not build_exists:
                build_exists = True
                print("✓ Build folder created")

            if os.path.exists('dist') and not dist_exists:
                dist_exists = True
                print("✓ Dist folder created")

            last_check = current_time

        time.sleep(1)

    # Check if process completed successfully
    if process.returncode == 0:
        print("\n✅ Build completed successfully!")
        print(f"Your executable is in: {os.path.abspath('dist/Abu Mukh Car Parts')}")
    else:
        print("\n❌ Build failed with error code:", process.returncode)

except KeyboardInterrupt:
    print("\nBuild cancelled by user.")
    process.kill()