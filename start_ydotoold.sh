#!/bin/bash

if pgrep -x "ydotoold" > /dev/null; then
    echo "ydotoold is already running (PID: $(pgrep -x ydotoold))"
    exit 0
fi

ydotoold &

exit 0
