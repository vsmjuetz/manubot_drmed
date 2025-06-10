#!/usr/bin/env bash

## autobuild.sh: automatically rebuild manuscript outputs and the webpage when content changes
## Depends on watchdog https://github.com/gorakhargosh/watchdog

watchmedo shell-command \
  --wait \
  --command='bash build/build.sh && manubot webpage' \
  content
