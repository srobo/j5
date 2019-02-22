from j5 import VERSION

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="j5",
    version=VERSION,
    author="Dan Trickey",
    author_email="contact@trickey.io",
    description="J5 Robotics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j5api/j5",
    package_data={"j5": ["py.typed"]},
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
)
