PushOverflow
============

Send Pushover notifications of new questions posted to StackExchange

### Installation and Requirements

PushOverflow has been written for Python (tested on Python3.2+ on Ubuntu). 

Requires [Requests](http://docs.python-requests.org/en/latest/). Installation instructions are [here](http://docs.python-requests.org/en/latest/user/install.html#install), but in short:
```
$ pip install requests
```

### Setup

- Copy and rename `pushoverflow.ini.sample` to `pushoverflow.ini` and edit the configuration for the StackExchange sites you would like notifications. `tags` allows you to filter questions with one of those tags (comma separated tags treated as boolean OR). `exclude` will filter out questions with any oof those tags. Both are optional.

  Each configuration section will check a specific StackExchange site. For instance `[scifi]` will check for new questions in http://scifi.stackexchange.com/ (Science Fiction & Fantasy).

- You will need to specify your Pushover user key in the configuration (in `userkey`), as well as [register an application](https://pushover.net/api#registration) with Pushover and specify the application's API token (in `appkey`).

- Set `time_delta_minutes` to the number of minutes you would like between each check.

- Setup a cron job (`crontab -e`) to run `pushoverflow.py` with the same frequency as `time_delta_minutes`.

  Eg. For `time_delta_minutes = 20`:

  ```
  */20 * * * * cd /path/to/pushoverflow && ./pushoverflow.py
  ```

### Todo

- Some code cleanup
- Allow boolean AND of multiple tags
- Look into more Pushover options
