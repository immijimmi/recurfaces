from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="recurfaces",
    packages=[
        "recurfaces"
    ],
    version="2.3.0",
    license="MIT",
    description="A pygame framework used to organise Surfaces into a chain structure",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="immijimmi",
    author_email="immijimmi1@gmail.com",
    url="https://github.com/immijimmi/recurfaces",
    download_url="https://github.com/immijimmi/recurfaces/archive/refs/tags/v2.2.0.tar.gz",
    keywords=["ui", "gui", "graphical", "user", "interface", "game"],
    install_requires=[
        "pygame~=2.5.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: pygame",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
)
