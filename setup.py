# -*- coding: utf-8 -*-
# https://packaging.python.org/tutorials/packaging-projects/
from pathlib import Path

import setuptools  # type: ignore


with Path("README.md").open("r") as fh_read_me:
    READ_ME = fh_read_me.read()

setuptools.setup(
    name="PAN",
    version="0.8.1",
    author="Artur Lissin",
    author_email="arturOnRails@protonmail.com",
    description="Library for using artificial neural networks.",
    long_description=READ_ME,
    long_description_content_type="text/markdown",
    url="",
    license='MIT License',
    packages=setuptools.find_packages(),
    python_requires="==3.8",
    install_requires=[
        'ReWoWr == 0.8.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License"
    ],
    zip_safe=False
)
