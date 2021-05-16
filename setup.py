import setuptools

setuptools.setup(
    name="github-cli",
    version="1.0",
    author="Christopher Sullivan",
    author_email="csullivannet@users.noreply.github.com",
    description="Playing around with the GitHub API in a python CLI.",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["cli = cli.cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
