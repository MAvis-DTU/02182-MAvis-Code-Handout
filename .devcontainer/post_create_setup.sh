# !/bin/bash

# Find workspace folder and add it as safe directory
WORKSPACE=$(find /workspaces -mindepth 1 -maxdepth 1 -type d | head -n 1)
git config --global --add safe.directory "$WORKSPACE"

# Installing search and robot locally
pip3 install -e .