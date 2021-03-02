import setuptools  # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "0.9.7"

setuptools.setup(
    name="abstractcp",
    version=VERSION,
    author="Claude El",
    author_email="abstractcp@claude.nl",
    description="Create abstract class variables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reinhrst/abstractcp",
    packages=setuptools.find_packages(),
    package_data={"abstractcp": ["py.typed"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
