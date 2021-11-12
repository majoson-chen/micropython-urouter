from setuptools import setup
from pathlib import Path

__version__: str
# get version
with (Path('.') / 'urouter' / '__init__.py').open('r') as fp:
    while True:
        line = fp.readline()
        if line.startswith("__version__"):
            exec(line)
            break

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="micropython-urouter",
    version=__version__,

    packages=['urouter'],
    install_requires=['micropython-ulogger'],
    # requirements=['micropython-ulogger'],
    include_package_data=True,

    author="Youkii-Chen",
    author_email="youkii-chen@qq.com",
    description="A simple, lightweight, fast, and flexible WEB framework designed for embedded devices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Youkii-Chen/micropython-urouter",
    project_urls={
        "Bug Tracker": "https://github.com/Youkii-Chen/micropython-urouter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="micropython",

)
