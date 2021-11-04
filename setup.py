from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="recurfaces",
    packages=[
        "recurfaces"
    ],
    version="0.4.0",
    license="LGPLv3",
    description="A pygame framework used to organise Surfaces into a chain structure",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="immijimmi",
    author_email="imranhamid99@msn.com",
    url="https://github.com/immijimmi/recurfaces",
    download_url="https://github.com/immijimmi/recurfaces/archive/refs/tags/v0.4.0.tar.gz",
    keywords=["ui", "gui", "graphical", "user", "interface", "game"],
    install_requires=[
        "pygame~=2.0.1"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.6",
    ],
)
