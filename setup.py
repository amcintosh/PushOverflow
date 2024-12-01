from setuptools import setup, find_packages
import pushoverflow

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("freshbooks/VERSION") as f:
    version = f.readlines()[0].strip()

setup(
    name="pushoverflow",
    version=version,
    author="Andrew McIntosh",
    author_email="andrew@amcintosh.net",
    description="Pushover Notifications for StackExchange Sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amcintosh/PushOverflow",
    download_url=f"https://github.com/amcintosh/PushOverflow/archive/refs/tags/{pushoverflow.__version__}.tar.gz",
    keywords=["stackexchange", "pushover", "notifications"],
    license="MIT",
    packages=find_packages(exclude=["tests", "*.test", "*.test.*"]),
    include_package_data=True,
    install_requires=open("requirements.txt").readlines(),
    entry_points={
        "console_scripts": [
            "pushoverflow=pushoverflow.cli:main"
        ]
    },
    test_suite="tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ]
)
