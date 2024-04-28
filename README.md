<img src="https://i.imgur.com/eE3DF1o.png" width="550">

# Stack Overflow Watchman
![Python 2.7 and 3 compatible](https://img.shields.io/pypi/pyversions/stack-overflow-watchman)
![PyPI version](https://img.shields.io/pypi/v/stack-overflow-watchman.svg)
![License: MIT](https://img.shields.io/pypi/l/stack-overflow-watchman.svg)

Monitoring Stack Overflow Enterprise for exposed secrets

## About Stack Overflow Watchman
Stack Overflow Watchman is an application that uses the Stack Overflow for Teams API to find potentially sensitive data exposed in a Stack Overflow Enterprise for Teams site.

More information about Stack Overflow Watchman can be found [on my blog](https://papermtn.co.uk/category/tools/stack-overflow-watchman/).

### Features
Stack Overflow Watchman looks for:

- API Keys, Tokens & Service Accounts
  - AWS, Azure, GCP, Google API, Slack (keys & webhooks), Twitter, Facebook, GitHub and more
  - Generic Private keys
  - Access Tokens, Bearer Tokens, Client Secrets, Private Tokens
  - Leaked passwords
  - Passport numbers, Dates of birth, Social security numbers, National insurance numbers and more

#### Time based searching
You can run Stack Overflow Watchman to look for results going back as far as:
- 24 hours
- 7 days
- 30 days
- All time

This means after one deep scan, you can schedule Stack Overflow Watchman to run regularly and only return results from your chosen timeframe.

### Signatures
Stack Overflow Watchman uses custom YAML signatures to detect matches in Stack Overflow for Teams. These signatures are pulled from the central [Watchman Signatures repository](https://github.com/PaperMtn/watchman-signatures). Stack Overflow Watchman automatically updates its signature base at runtime to ensure its using the latest signatures to detect secrets.

### Logging

Stack Overflow Watchman gives the following logging options:
- Terminal-friendly Stdout
- JSON to Stdout

Stack Overflow Watchman defaults to terminal-friendly stdout logging if no option is given. This is designed to be easier for humans to read.

JSON logging is also available, which is perfect for ingesting into a SIEM or other log analysis platforms.

JSON formatted logging can be easily redirected to a file as below:
```commandline
stack-overflow-watchman --timeframe a --all --output json >> stack_overflow_watchman_log.json 
```

## Authentication Requirements
### Stack Overflow API token
To run Stack Overflow Watchman, you will need an API token. You can create this in your Stack Overflow for Teams account under `Account -> Settings -> API Applications`. Create a new application and copy the token from the details pane.

You will also need the domain of the Stack Overflow for Teams site. If your site is `papermtn.stackoverflow.co`, then the domain is `papermtn`.
#### Providing Token & URL
Pass the URL and Token to Stack Overflow Watchman via the environment variables: 
- `STACK_OVERFLOW_WATCHMAN_TOKEN`
- `STACK_OVERFLOW_WATCHMAN_DOMAIN`

## Installation
You can install the latest stable version via pip:

```commandline
python3 -m pip install stack-overflow-watchman
```

Or build from source yourself:

Download the release source files, then from the top level repository run:
```commandline
python3 -m pip build
python3 -m pip install --force-reinstall dist/*.whl
```

## Docker Image

Stack Overflow Watchman is also available from the Docker hub as a Docker image:

`docker pull papermountain/stack-overflow-watchman:latest`

You can then run Stack Overflow Watchman in a container, making sure you pass the required environment variables:

```commandline
// help
docker run --rm papermountain/stack-overflow-watchman -h

// scan all
docker run --rm -e STACK_OVERFLOW_WATCHMAN_TOKEN=abc... -e STACK_OVERFLOW_WATCHMAN_DOMAIN=papermtn papermountain/stack-overflow-watchman --timeframe a --all --output json
docker run --rm --env-file .env papermountain/stack-overflow-watchman --timeframe a --all --output stdout
```

## Usage
Stack Overflow Watchman will be installed as a global command, use as follows:
```commandline
usage: stack-overflow-watchman [-h] [--timeframe {d,w,m,a}] [--output {json,stdout}] [--version] [--debug]

options:
  -h, --help            show this help message and exit
  --timeframe {d,w,m,a}
                        How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time. Defaults to all time
  --output {json,stdout}, -o {json,stdout}
                        Where to send results
  --version, -v         show program's version number and exit
  --debug, -d           Turn on debug level logging
  ```

You can run Stack Overflow Watchman to look for everything, and output to default stdout:

```commandline
stack-overflow-watchman --timeframe a --all
```

## Other Watchman apps
You may be interested in the other apps in the Watchman family:
- [Slack Watchman](https://github.com/PaperMtn/slack-watchman)
- [Slack Watchman for Enterprise Grid](https://github.com/PaperMtn/slack-watchman-enterprise-grid)
- [GitLab Watchman](https://github.com/PaperMtn/gitlab-watchman)
- [GitHub Watchman](https://github.com/PaperMtn/github-watchman)

## License
The source code for this project is released under the [GNU General Public Licence](https://www.gnu.org/licenses/licenses.html#GPL). This project is not associated with Stack Overflow.