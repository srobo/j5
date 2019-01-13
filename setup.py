import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="j5",
    version="0.0.1",
    author="Dan Trickey",
    author_email="contact@trickey.io",
    description="J5 Robotics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j5api/j5",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
)
