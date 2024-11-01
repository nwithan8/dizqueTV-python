import json
import os
from typing import List

import setuptools

from dizqueTV._info import __version__


__title__ = "dizqueTV"
__author__ = 'Nate Harris'
__author_email__ = 'n8gr8gbln@gmail.com'
__github_username__ = "nwithan8"
__github_repo__ = "dizqueTV-python"
__copyright__ = "Copyright © YEARADDEDBYGITHUB - Nate Harris"
__license__ = 'GNU General Public License v3 (GPLv3)'
__docs__ = "https://dizquetv.readthedocs.io/en/latest"
__description__ = "Interact with a dizqueTV instance's API"
__keywords__ = [
    "dizqueTV",
    "Plex",
    "Jellyfin",
    "Emby",
    "media",
    "API",
    "server",
    "interaction",
    "TV",
    "television",
    "streaming",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    REQUIREMENTS = fh.read().splitlines()

with open("dev_requirements.txt", "r") as fh:
    DEV_REQUIREMENTS = fh.read().splitlines()


def __supported_python_versions__() -> List[str]:
    """Return a list of supported Python versions."""
    with open(os.path.join(os.path.dirname(__file__), "dizqueTV", "PYTHON_VERSIONS.json")) as f:
        versions = f.read()
        return json.loads(versions)


def python_versions() -> List[str]:
    """Return a list of supported Python versions."""
    versions = __supported_python_versions__()
    version_strings = ['Programming Language :: Python :: 3']
    for version in versions:
        version_strings.append(f"Programming Language :: Python :: {version}")
    return version_strings


def python3_range() -> str:
    """Return a string of the supported Python version range."""
    versions = __supported_python_versions__()
    return f">={versions[0]}, <4"


classifiers = [
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Development Status :: 4 - Beta',
    # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',  # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'Topic :: Multimedia :: Video',
    'Topic :: Multimedia',
    'Topic :: Internet :: WWW/HTTP',
    'Operating System :: OS Independent'
]
classifiers.extend(python_versions())

# Replace version if not replaced already
try:
    _ = setuptools._vendor.packaging.version.Version(__version__)
except Exception:
    if "." in __version__:  # If __version__ was replaced by GitHub Actions, but could not be converted to a version
        __version__ = 'VERSIONADDEDBYGITHUB'  # Will be replaced by GitHub Actions with actual version number
    else:
        __version__ = "0.0.0"  # If __version__ was not replaced by GitHub Actions, set to 0.0.0

setuptools.setup(
    name=__title__,
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    version=__version__,
    license=__license__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__author_email__,
    url=f'https://github.com/{__github_username__}/{__github_repo__}',
    download_url=f'https://github.com/{__github_username__}/{__github_repo__}/archive/refs/tags/{__version__}.tar.gz',
    keywords=__keywords__,
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    test_suite="test",
    classifiers=classifiers,
    python_requires=python3_range(),
)
