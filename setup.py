from setuptools import setup, find_packages
import sys
import pushoverflow

ver = sys.version_info
if ver[0] == 2 or (ver[0] == 3 and ver[1] == 2):
    requirements = "requirements27-32.txt"
else:
    requirements = "requirements.txt"

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
    install_requires=open(requirements).readlines(),
    entry_points={
        "console_scripts": [
            "pushoverflow=pushoverflow.cli:main"
        ]
    },
    test_suite="tests"
)
