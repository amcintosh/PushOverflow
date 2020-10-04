from setuptools import setup, find_packages
import pushoverflow

setup(
    name="pushoverflow",
    version=pushoverflow.__version__,
    author=pushoverflow.__author__,
    author_email="andrew@amcintosh.net",
    description="Pushover Notifications for StackExchange Sites",
    long_description=open("README.rst").read(),
    url="https://github.com/amcintosh/PushOverflow",
    download_url=("https://github.com/amcintosh/PushOverflow/tarball/%s" %
                  pushoverflow.__version__),
    keywords=["stackexchange", "pushover", "notifications"],
    license=pushoverflow.__license__,
    packages=find_packages(exclude=["*.test", "*.test.*"]),
    include_package_data=True,
    install_requires=open("requirements.txt").readlines(),
    entry_points={
        "console_scripts": [
            "pushoverflow=pushoverflow.cli:main"
        ]
    },
    test_suite="tests"
)
