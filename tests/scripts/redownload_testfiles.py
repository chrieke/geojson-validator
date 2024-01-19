# Downloads example files from https://github.com/chrieke/geojson-invalid-geometry to ./tests/data

from pathlib import Path
import requests

TESTFILES_DIR = Path("tests/data/")

# GitHub repository details
USER = "chrieke"
REPO = "geojson-invalid-geometry"
BRANCH = "main"
FOLDERS = [
    "examples/invalid_geometries",
    "examples/problematic_geometries",
    "examples/valid",
    "examples/invalid_structure",
    "examples/problematic_structure",
]

# GitHub API URL for contents
API_BASE_URL = f"https://api.github.com/repos/{USER}/{REPO}/contents/"


def download_file(url, local_path):
    response = requests.get(url, timeout=5)
    local_path.write_bytes(response.content)


def download_folder_contents(folder):
    folder_url = f"{API_BASE_URL}{folder}?ref={BRANCH}"
    response = requests.get(
        folder_url, timeout=5
    )  # Include auth token in headers if needed
    items = response.json()

    for item in items:
        print(f"Downloading {item['name']} ...")
        if item["type"] == "file" and item["name"].endswith(".geojson"):
            file_url = item["download_url"]
            base_folder_name = str(Path(folder).name)
            local_path = TESTFILES_DIR / base_folder_name / item["name"]
            download_file(file_url, local_path)
            print(f"Downloaded {item['name']} to {local_path}")


def main():
    for folder in FOLDERS:
        base_folder_name = str(Path(folder).name)
        folder_path = TESTFILES_DIR / base_folder_name
        if folder_path.exists():
            raise ValueError(f"Folder {folder_path} already exists. Delete manually.")
        folder_path.mkdir(parents=True)
        download_folder_contents(folder)


if __name__ == "__main__":
    main()
