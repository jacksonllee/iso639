import os
import re

import iso639


_REPO_DIR = os.path.dirname(os.path.dirname(__file__))


def test_version_number_match_with_changelog():
    """__version__ and CHANGELOG.md match for the latest version number."""
    changelog = open(os.path.join(_REPO_DIR, "CHANGELOG.md"), encoding="utf-8").read()
    # latest version number in changelog = the 1st occurrence of '[x.y.z]'
    version_in_changelog = (
        re.search(r"\[\d+\.\d+\.\d+\]", changelog).group().strip("[]")
    )
    if "dev" in iso639.__version__:
        # CHANGELOG.md doesn't update the section headings for dev versions,
        # and so iso639.__version__ with "dev" (e.g., "3.1.0dev1")
        # wouldn't match any version headings in CHANGELOG.md.
        return
    assert iso639.__version__ == version_in_changelog, (
        "Make sure both __version__ and CHANGELOG are updated to match the "
        "latest version number"
    )


def test_no_zero_padding():
    version: str = iso639.__version__
    assert re.fullmatch(
        r"\A\d+\.\d+\.\d+\Z", version
    ), f"Unexpected version number format: {version}"
    for v, label in zip(version.split("."), ("major", "minor", "micro")):
        assert (
            v.lstrip("0") == v
        ), f"{label} version number '{v}' has disallowed zero padding."
