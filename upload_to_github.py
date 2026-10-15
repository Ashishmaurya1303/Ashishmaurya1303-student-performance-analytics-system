
import os
from getpass import getpass
from github import Github, Auth
from github.GithubException import UnknownObjectException

USERNAME = "Ashishmaurya1303"
REPO_NAME = "student-performance-analytics-system"
PROJECT_DIR = r"E:\Python with ai\student_analytics_system"

token = getpass("Paste GitHub token (input hidden): ")
gh = Github(auth=Auth.Token(token))

try:
    repo = gh.get_repo(f"{USERNAME}/{REPO_NAME}")
    print("Connected to:", repo.full_name)

    skip_dirs = {
        ".git", "__pycache__", ".venv", "venv",
        "env", "node_modules"
    }
    skip_files = {".env", ".env.local", ".env.production"}

    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            if filename in skip_files or filename.endswith(".pyc"):
                continue

            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(
                full_path, PROJECT_DIR
            ).replace("\\", "/")

            if relative_path.split("/")[0] == "data":
                print("Skipped data folder:", relative_path)
                continue

            if os.path.getsize(full_path) > 90 * 1024 * 1024:
                print("Skipped large file:", relative_path)
                continue

            try:
                with open(full_path, "rb") as f:
                    content = f.read()

                try:
                    existing = repo.get_contents(relative_path)
                    if isinstance(existing, list):
                        print("Skipped directory:", relative_path)
                        continue
                    repo.update_file(
                        relative_path, "Update " + relative_path,
                        content, existing.sha
                    )
                except UnknownObjectException:
                    repo.create_file(
                        relative_path, "Add " + relative_path, content
                    )

                print("Uploaded:", relative_path)

            except Exception as e:
                print("FAILED:", relative_path, "-", e)

    print("Upload process finished.")
    print("Repository:", repo.html_url)
finally:
    gh.close()
