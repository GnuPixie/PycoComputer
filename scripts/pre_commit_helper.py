import subprocess
import sys


def main():
    """
    A cross-platform helper for pre-commit.
    1. Runs the 'pixi run fmt' command.
    2. If formatting is successful, stages the changes with 'git add -u'.
    """
    print("Running formatter...")
    # Use 'shell=True' on Windows to help find executables in the PATH.
    is_windows = sys.platform == "win32"
    result = subprocess.run(["pixi", "run", "fmt"], shell=is_windows)

    # If formatting fails (e.g., syntax error), abort the commit.
    if result.returncode != 0:
        print("Formatting failed. Aborting commit.", file=sys.stderr)
        return result.returncode

    print("Staging formatted files...")
    # Stage any files modified by the formatter.
    subprocess.run(["git", "add", "-u"], shell=is_windows)

    return 0


if __name__ == "__main__":
    sys.exit(main())
