# !/bin/bash

# Add workspace folder as safe directory allowing vscode's
# git extension to work inside the container.
git config --global --add safe.directory "/workspaces/mavis_client"

# Installing search and robot locally via uv
uv sync