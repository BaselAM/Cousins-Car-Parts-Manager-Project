import os

# Folders to ignore
IGNORE_FOLDERS = {"venv", "venv_38", "node_modules", "__pycache__", ".git", ".idea", ".vscode", "dist", "build", "__MACOSX"}

def print_tree(startpath, depth=4, prefix=""):
    """Prints the project structure up to the specified depth."""
    if depth < 1:
        return

    try:
        items = sorted(
            [item for item in os.listdir(startpath) if item not in IGNORE_FOLDERS],
            key=lambda s: (not os.path.isdir(os.path.join(startpath, s)), s.lower())
        )
    except PermissionError:
        return  # Skip folders we can't open

    total = len(items)
    for index, item in enumerate(items):
        path = os.path.join(startpath, item)
        connector = "└── " if index == total - 1 else "├── "
        print(prefix + connector + item)

        if os.path.isdir(path):
            new_prefix = prefix + ("    " if index == total - 1 else "│   ")
            print_tree(path, depth - 1, new_prefix)

# Replace with your actual project folder path
project_root = r"C:\Users\97253\Desktop\BeastMode-CSIntro-Excercises\CousinTestProject"

print(os.path.basename(project_root))
print_tree(project_root, depth=4)
