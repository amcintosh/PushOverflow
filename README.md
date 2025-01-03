# PushOverflow

[![PyPI](https://img.shields.io/pypi/v/pushoverflow)](https://pypi.org/project/pushoverflow/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pushoverflow)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/amcintosh/pushoverflow/run-tests.yml?branch=main)](https://github.com/amcintosh/pushoverflow/actions?query=workflow%3A%22Run+Tests%22)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1cd16cda0531412c8cd6eee0c217688a)](https://app.codacy.com/gh/amcintosh/PushOverflow/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

Send Pushover notifications of new questions posted to StackExchange

## Installation

To install:

```shell
pip install pushoverflow
```

## Setup

- Copy and rename `pushoverflow.ini.sample` to `pushoverflow.ini`. By default PushOverflow will look
  for the file in the current directory (eg. `./pushoverflow.ini`) or you can specify the path at runtime
  (eg. `pushoverflow /path/to/pushoverflow.ini`).

- Edit the configuration for the StackExchange sites you would like notifications. `tags` allows you to
  filter questions with one of those tags (comma separated tags treated as boolean OR). `exclude` will
  filter out questions with any oof those tags. Both are optional.

  Each configuration section will check a specific StackExchange site. For instance `[scifi]` will check
  for new questions in http://scifi.stackexchange.com/ (Science Fiction & Fantasy).

- You will need to specify your Pushover user key in the configuration (in `userkey`), as well as
  [register an application](https://pushover.net/api#registration) with Pushover and specify the
  application's API token (in `appkey`).

- Set `time_delta_minutes` to the number of minutes you would like between each check.

- Setup a cron job (`crontab -e`) to run `pushoverflow.py` with the same frequency as `time_delta_minutes`.
  Eg. For `time_delta_minutes = 20`:

  ```txt
  */20 * * * * pushoverflow /path/to/config_file
  ```

  or

  ```txt
  */20 * * * * cd /path/to/config_directory && pushoverflow
  ```

### Future Ideas

- Allow boolean AND of multiple tags
- More granular priority settings
