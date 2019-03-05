import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="j5",
    version="0.0.2",
    author="j5 Contributors",
    author_email="sro@soton.ac.uk",
    description="J5 Robotics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j5api/j5",
    package_data={"j5": ["py.typed"]},
    packages=['j5'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Typing :: Typed",
        "Topic :: Education",
    ],
)
