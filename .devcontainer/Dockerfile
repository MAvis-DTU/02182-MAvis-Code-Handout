FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install basic development tools
RUN apt update && apt install -y less man-db sudo
RUN apt-get update

# Install server dependencies
RUN apt-get install -y libxi6 libgconf-2-4 libxtst6 openjdk-17-jre ffmpeg

# Install graphviz
RUN apt-get install -y graphviz --fix-missing

# Copy requirements files
COPY requirements*.txt /tmp/

# Install client dependencies
RUN pip3 install -r /tmp/requirements.txt

# Activate argcomplete
RUN activate-global-python-argcomplete

# Install student defined dependencies.
# Separated to improve the caching of the build steps.
RUN pip3 install -r /tmp/requirements.students.txt

# Set `DEVCONTAINER` environment variable to help with orientation
ENV DEVCONTAINER=true