import subprocess


def run():
    commands = [
        ["isort", "--profile", "black", "--project=ai_plays_jackbox", "."],
        ["black", "-l", "120", "."],
    ]

    for cmd in commands:
        print(f"\n>>> Running: {' '.join(cmd)}")
        subprocess.run(["poetry", "run"] + cmd, check=True)
