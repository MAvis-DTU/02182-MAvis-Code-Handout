FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install basic development tools
RUN apt update && apt install -y less man-db sudo
RUN apt-get update

# Install server dependencies
RUN apt-get install -y libxi6 libgconf-2-4 libxtst6 openjdk-17-jre

# Install python 2
RUN apt-get install -y python python2.7-dev build-essential libpython2.7

# Install robot client dependencies (naoqi)
RUN wget https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz -O /tmp/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
RUN mkdir -p /home/vscode/packages
RUN tar -xf /tmp/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz -C /home/vscode/packages
RUN mv /home/vscode/packages/pynaoqi-python2.7-2.5.7.1-linux64 /home/vscode/packages/pynaoqi-python2.7
ENV PYTHONPATH=/home/vscode/packages/pynaoqi-python2.7/lib/python2.7/site-packages
RUN chown -R vscode:vscode /home/vscode/packages

# Install pip2
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o /tmp/get-pip.py
RUN python2 /tmp/get-pip.py

# Copy requirements files
COPY requirements*.txt /tmp/

# Install robot server dependencies
RUN pip2 install -r /tmp/requirements.robotserver.txt

# Install search client dependencies
RUN pip3 install -r /tmp/requirements.searchclient.txt

# Set `DEVCONTAINER` environment variable to help with orientation
ENV DEVCONTAINER=true