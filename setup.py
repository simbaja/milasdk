import pathlib
from setuptools import setup, find_namespace_packages

try:
    import re2 as re
except ImportError:
    import re

base_package = "milasdk"

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Pull the version from __init__.py so we don't need to maintain it in multiple places
init_txt = (HERE / base_package / "__init__.py").read_text("utf-8")
try:
    version = re.findall(r"^__version__ = ['\"]([^'\"]+)['\"]\r?$", init_txt, re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')

# This call to setup() does all the work
setup(
    name="milasdk",
    version=version,
    description="Python SDK for Mila Air Purifiers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/simbaja/milasdk",
    author="Jack Simbach",
    author_email="jack.simbach@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_namespace_packages(include=[base_package, f"{base_package}*"]),
    include_package_data=False,
    install_requires=["aiohttp", "magicattr", "gql", "StrEnum"]
)
