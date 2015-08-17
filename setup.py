from setuptools import setup, find_packages
import sys
import pushoverflow

if sys.version_info[0] == 2:
    requirements = "requirements27.txt"
else:
    requirements = "requirements.txt"

setup(
    name="pushoverflow",
    version=pushoverflow.__version__,
    author=pushoverflow.__author__,
    description="Pushover Notifications for StackExchange Sites",
    url="https://github.com/amcintosh/PushOverflow",
    license=pushoverflow.__license__,
    packages=find_packages(exclude=["*.test", "*.test.*"]),
    include_package_data=True,
    install_requires=open(requirements).readlines(),
    entry_points={
        "console_scripts": [
            "pushoverflow=pushoverflow.cli:main"
        ]
    },
    test_suite="tests",
    tests_require=["httpretty", "mock"]
)
