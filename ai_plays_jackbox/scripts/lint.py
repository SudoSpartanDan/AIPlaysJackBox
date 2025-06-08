import subprocess


def run():
    commands = [
        ["autoflake", "--in-place", "--recursive", "--remove-all-unused-imports", "--verbose", "ai_plays_jackbox"],
        ["isort", "--profile", "black", "--project=ai_plays_jackbox", "ai_plays_jackbox"],
        ["black", "-l", "120", "ai_plays_jackbox"],
        ["mypy", "ai_plays_jackbox"],
    ]

    for cmd in commands:
        print(f"\n>>> Running: {' '.join(cmd)}")
        subprocess.run(["poetry", "run"] + cmd, check=True)


if __name__ == "__main__":
    run()
