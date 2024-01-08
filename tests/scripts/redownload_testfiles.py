# Downloads testfiles from https://github.com/chrieke/geojson-invalid-geometry

from pathlib import Path
import requests

testfiles_dir = Path("tests/data/")

# GitHub repository details
user = "chrieke"
repo = "geojson-invalid-geometry"
branch = "main"
folders = [
    "examples_geojson/invalid",
    "examples_geojson/problematic",
    "examples_geojson/valid",
]

# GitHub API URL for contents
api_base_url = f"https://api.github.com/repos/{user}/{repo}/contents/"


def download_file(url, local_path):
    response = requests.get(url, timeout=5)
    local_path.write_bytes(response.content)


def download_folder_contents(folder):
    folder_url = f"{api_base_url}{folder}?ref={branch}"
    response = requests.get(
        folder_url, timeout=5
    )  # Include auth token in headers if needed
    items = response.json()

    for item in items:
        if item["type"] == "file" and item["name"].endswith(".geojson"):
            file_url = item["download_url"]
            local_path = testfiles_dir / folder / item["name"]
            print(f"Downloading {item['name']} to {local_path}")
            download_file(file_url, local_path)


def main():
    for folder in folders:
        folder_path = testfiles_dir / folder
        if folder_path.exists():
            raise ValueError(
                f"Folder {folder_path} already exists. Delete 'examples_geojson' folder manually."
            )
        folder_path.mkdir(parents=True)
        download_folder_contents(folder)


if __name__ == "__main__":
    main()
