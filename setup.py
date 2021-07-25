from setuptools import setup
from urouter import __version__
from os import path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="micropython-urouter",
    version=__version__,

    packages=['urouter'],
    requirements=['micropython-ulogger'],

    author="M-Jay",
    author_email="m-jay-1376@qq.com",
    description="A simple, lightweight, fast, and flexible WEB framework designed for embedded devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Li-Lian1069/micropython-urouter",
    project_urls={
        "Bug Tracker": "https://github.com/Li-Lian1069/micropython-urouter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="micropython",

)
