#!/usr/bin/env bash
echo "---------- start app stop -------------"

pkill -INT gunicorn

echo "---------- finish app stop -------------"
