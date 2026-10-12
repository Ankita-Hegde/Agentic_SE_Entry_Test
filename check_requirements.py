import json
import urllib.request
import urllib.error


def get_json(url):
    """Return the JSON from a PyPI URL, or None if PyPI says 404 (not found)."""
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise  # any other error is a real problem, not "missing"


def main():
    with open("requirements.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    packages_missing = 0
    versions_missing = 0
    oldest = None  # (upload_time, name, version)

    for line in lines:
        name, version = line.split("==")
        name, version = name.strip(), version.strip()

        # Step 1: does the package exist?
        if get_json(f"https://pypi.org/pypi/{name}/json") is None:
            packages_missing += 1
            continue

        # Step 2: does the pinned version exist?
        release = get_json(f"https://pypi.org/pypi/{name}/{version}/json")
        if release is None:
            versions_missing += 1
            continue

        # Step 3: upload time of the first file, keep the oldest
        if release["urls"]:
            upload_time = release["urls"][0]["upload_time"]
            if oldest is None or upload_time < oldest[0]:
                oldest = (upload_time, name, version)

    print(f"Dependencies checked: {len(lines)}")
    print(f"Packages not on PyPI: {packages_missing}")
    print(f"Versions not on PyPI: {versions_missing}")
    if oldest:
        upload_time, name, version = oldest
        print(f"Oldest pinned release: {name}=={version} ({upload_time[:4]})")


if __name__ == "__main__":
    main()
