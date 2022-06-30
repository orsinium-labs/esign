# esign.py

Python CLI tool for signing Jira issues in [eSign](https://digitalrose.atlassian.net/wiki/spaces/ESIGN/overview) Jira plugin.

## Usage

To obtain the token, you need to open Jira in your browser, find the value of `cloud.session.token` cookie, copy it, and save it somewhere. I store it in `.token` file. To sign an issue, you need to run something like this:

```bash
python3 esign.py \
    --issue     PROJ-1234       \
    --meaning   "Code Review"   \
    --company   acme-corp       \
    --pin       123456          \
    --token     $(cat .token)   \
    --finalize
```

That's verbose but most of the arguments will be the same. The purpose of the script is to be used in combination with [go-jira](https://github.com/go-jira/jira) to fully automate signing issues. See [Taskfile.yml](./Taskfile.yml) for a real-world example.
