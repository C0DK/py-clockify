import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="pyclockify",
    version="0.0.1",
    author="Casper Weiss Bang",
    author_email="master@thecdk.net",
    description="A package for integrations with the time tracking service, Clockify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/C0DK/py-clockify",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
