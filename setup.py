from setuptools import setup, find_packages
import os.path

pwd = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(pwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="nxdomain",
    version="1.0.0",
    description="Downloads and converts domain block lists for use with BIND/named RPZ files or dnsmasq host files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zopieux/nxdomain",
    author="Alexandre Macabies",
    author_email="web@zopieux.com",
    install_requires=["dnspython~=2.0"],
    packages=find_packages(),
    project_urls={
        "Bug Reports": "https://github.com/zopieux/nxdomain/issues",
        "Source": "https://github.com/zopieux/nxdomain",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    zip_safe=True,
    include_package_data=True,
)
