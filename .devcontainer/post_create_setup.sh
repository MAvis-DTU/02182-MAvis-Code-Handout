# !/bin/bash

# Find workspace folder and add it as safe directory
WORKSPACE=$(find /workspaces -mindepth 1 -maxdepth 1 -type d | grep "02182" | head -n 1)
git config --global --add safe.directory "$WORKSPACE"

# Installing search locally
pip3 install -e .devcontainer/