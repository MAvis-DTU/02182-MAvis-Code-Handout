# MAvis - 02182

This repository contains content for the MAvis assignments of the DTU course: Symbolic artificial intelligence - 02182, and is considered DTU property.

This README includes guides for setting up your own private downstream repository, installing the requirements, how to use the client and server, how to interface with the Pepper robots.

## Table of contents
- [Table of contents](#table-of-contents)
- [Private repository setup](#private-repository-setup)
- [Requirements](#requirements)
- [Devcontainer](#devcontainer)
  - [Setup](#setup)
  - [Tips \& Troubleshooting](#tips--troubleshooting)
    - [Selecting python interpreter](#selecting-python-interpreter)
  - [Adding pip packages](#adding-pip-packages)
  - [(noVNC) changing the resolution of the virtual environment](#novnc-changing-the-resolution-of-the-virtual-environment)
  - [X11 Problems](#x11-problems)
- [Client](#client)
  - [Agent types](#agent-types)
  - [Debugging](#debugging)
  - [Memory settings](#memory-settings)
- [Interactive documentation](#interactive-documentation)
- [Pepper robot guide](#pepper-robot-guide)
  - [Connecting to the Pepper network](#connecting-to-the-pepper-network)
  - [Turning on Pepper](#turning-on-pepper)
  - [Getting Pepper IP address](#getting-pepper-ip-address)
  - [Connecting to Pepper](#connecting-to-pepper)
  - [Putting Pepper to sleep/hibernate](#putting-pepper-to-sleephibernate)
  - [Turning Pepper off](#turning-pepper-off)
  - [Localization](#localization)
  - [Whisper Speech Recognition](#whisper-speech-recognition)
  - [Adding new functionality](#adding-new-functionality)


## Private repository setup

To setup your own private repository for your group work, follow these steps:

1. Create an empty private repo. It is absolutely crucial that this repo is *private*.
2. Bare clone the handout repo, and mirror push it to your private repo:
```shell
git clone --bare https://github.com/MAvis-DTU/02182-MAvis-Code-Handout.git
cd 02182-MAvis-Code-Handout.git
git push --mirror https://github.com/dtu-student-123/your-repo.git
cd ..
# Linux based systems
rm -rf 02182-MAvis-Code-Handout.git
# Powershell
rm -r -fo 02182-MAvis-Code-Handout.git
```
3. Add handout repository as a remote in your private repo:
```shell
git clone https://github.com/dtu-student-123/your-repo.git
cd your-repo
git remote add public https://github.com/MAvis-DTU/02182-MAvis-Code-Handout.git
```
4. From now on, every time you need to include new changes from the handout repo, run:
```shell
git pull public main
git push origin main
```

## Requirements
To simplify the installation of the requirements for this repo a [Devcontainer](#devcontainer) has been produces, which creates a virtual development environment with all the necessary requirements 
However if you want to install the dependencies locally the following section outlines what is required.

---

To complete assignments, it is required that you can execute Java programs compiled for the most recent Java release. 
You should therefore make sure to have an updated version of a Java Development Kit (JDK) installed before the continuing. 
Both Oracle JDK and OpenJDK will do. Additionally, you should make sure your PATH variable is configured 
so that `java` is available in your command-line interface (command prompt/terminal). Run 
```shell
java -version
```
from the command line to check which version your path is set up to use. It should be the version you just installed.  

The Python client has been tested with Python 3.12, but should work with versions of Python above 3.10.
The client requires the pip packages outlined in the [Devcontainer](#devcontainer) section.

## Devcontainer
To simplify the setup and installation of required dependencies, a [devcontainer](https://containers.dev/overview) has been created. This [docker](https://www.docker.com/) based development environment ensures you have all the necessary dependencies installed, and that your groups environment is the same, thus avoiding the "It works on my computer" cliché.

The environment comes preconfigured with:
- **Java (OpenJDK 17)** – Access via `java`
- **Python 3.12** (for the client) – Access via `python3` - with the following pip dependencies, specified in [requirements.txt](.devcontainer/requirements.txt)
    - `psutil` to monitor its memory usage.
    - `debugpy` required to allow debugging through the java server
    - `numpy` to facilitate communication between the robot and the client
    - `scp` to transfer data (images & audio) to and from the robots
    - `qi` the Pepper SDK used to facilitate the communication with the robot
        - **Note** that this package is only available for Unix-based systems (MacOS & Linux)
    - `openai-whisper` to transcribe audio recordings, allowing verbal communication between user and robot.
    - Non-required packages:
        - `opencv-python` intended for manipulating image data from the robots
        - `pupil-apriltags` required to process apriltags
        - `graphviz` required to visualize solution graphs
        - `pdoc` required to run the [docs.py](docs.py) interactive code documentation
- **Graphviz** for visualizing solution graphs - Accessed through the python package.

### Setup
To setup the devcontainer the following **prerequisites** need to be installed:
1. [Docker](https://www.docker.com/)
    - **Note:** If you're using Windows, you may need to enable WSL2 and ensure your user has the correct Docker permissions.
2. [Visual studio code](https://code.visualstudio.com/)
3. The [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) vscode extension.
4. You have followed the [Private repository setup](#private-repository-setup)

With the prerequisites installed, follow these steps:
1. Open your repository in vscode
2. **IF EXPERIENCING X11 PROBLEMS:** Replace the natively x11 supporting configuration with the noVNC configuration in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
2. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
3. Run the `Dev Containers: Rebuild and Reopen in Container` command
    - The first build may take a while - check the logs to track progress.
    - Once your files appear in the Explorer (left panel), the devcontainer is ready.

**IF EXPERIENCING X11 PROBLEMS:** Some systems cannot efficiently run the server graphics natively. As a workaround [noVNC](https://novnc.com/info.html) have been used to forward the graphics via a webserver.    
To see the virtual GUI environment, open [localhost:8080/vnc.html](http://localhost:8080/vnc.html) and press connect.  

### Tips & Troubleshooting
#### Selecting python interpreter
As the client and the server uses different python versions, selecting the version you intend to use to run the code provides accurate [IntelliSense](https://code.visualstudio.com/docs/editor/intellisense), and ensures the right version is used if running it directly from vscode (`F5`).  
**Steps:**
1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
2. Run the `Python: Select Interpreter` command
3. Select the appropriate python version

### Adding pip packages
To ensure packages are installed when building or rebuilding the devcontainer, add wanted pip packages to the [.devcontainer/requirements.students.txt](.devcontainer/requirements.students.txt) file and rebuild the container (vscode command `Dev Containers: Rebuild Container`).

### (noVNC) changing the resolution of the virtual environment
1. Open [.devcontainer/docker-compose.yml](.devcontainer/docker-compose.yml)
2. Adjust the `DISPLAY_WIDTH` and `DISPLAY_HEIGHT` environment variables to your preference
3. Rebuild the devcontainer
    1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
    2. Run the `Dev Containers: Rebuild Container` command

### X11 Problems
1. Follow the noVNC setup steps, updating the [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
2. Rebuild the devcontainer
    1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
    2. Run the `Dev Containers: Rebuild Container` command
3. Access the GUI at [localhost:8080/vnc.html](http://localhost:8080/vnc.html)

## Client
All the following commands assume the working directory is the one this README is located in.

You can read about the server options using the -h argument:
```shell
java -jar server.jar -h
```

You can read about the client options using the `-h` flag:
```shell
python3 client.py -h
```

The client requires a agent type each with its own set of possible arguments and descriptions:
```shell
python3 client.py AGENT_TYPE -h
```

Running the server with the actions controlled by the client:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python3 client.py classic" -l levels/SAD1.lvl
```

For strategy based search the client uses BFS by default, but can be changed by providing the `--strategy` argument. For instance, to use DFS:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python3 client.py classic --strategy dfs" -l levels/SAD1.lvl
```

For astar and greedy, the `--heuristic` argument must be passed, specifying which heuristic to use for the strategy. There are currently two available: `goalcount` and `advanced`
For instance, to use astar search with the goalcount heuristic:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python3 client.py classic --strategy astar --heuristic goalcount" -l levels/SAD1.lvl
```

### Agent types
The `agents` folder contains agent types including:
- `classic` - A classic planning agent using GRAPH-SEARCH.
- `decentralised` - A planning agent using DECENTRALISED-AGENTS.
- `helper` - A planning agent using the helper agent algorithm.
- `nondeterministic` - A planning agent using AND-OR-GRAPH-SEARCH with a broken executor.
- `goalrecognition` - A planning agent using the all optimal plans for the actor and AND-OR-GRAPH-SEARCH for the helper
- `robot` - A planning agent which forwards the actions to a connected pepper robot.

### Debugging
As communication with the java server is performed over stdout, `print(<something>)` does not work directly. 
To get information sent to the terminal, you should use `sys.stderr` or the alias `print_debug` from the `search` module:
```python
print(<something>, file=sys.stderr)
# Or
from search import print_debug
print_debug(<something>)
```
Note that the State has a nice string representation such that you can print states to the terminal by writing
```python
print_debug(state)
```
For more advanced debugging using vscode and the devcontainer, simply add the `--debug` flag when running the server, e.g.:
```shell
java -jar server.jar -g -c "python3 client.py --debug classic" -l levels/SAD1.lvl
```
**Note that the server will still timeout if the `-t` argument is given.**

### Memory settings
*Unless your hardware is unable to support this, you should let the searchclient allocate at least 4GB of memory.*

The searchclient monitors its own process' memory usage and terminates the search if it exceeds a given number of MiB.

To set the max memory usage to 4GB:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python3 client.py --max-memory 4g classic" -l levels/SAD1.lvl
```
Avoid setting max memory usage too high, since it will lead to your OS doing memory swapping which is terribly slow.

## Interactive documentation
To host an interactive and searchable documentation of the code using its docstrings run:
```shell
python3 doc.py
```
This should host a webserver accessible via `http://localhost:8080` (port can be changed in `doc.py`).

## Pepper robot guide
### Connecting to the Pepper network
1. Ensure the network router has been plugged in. Ask a teacher or TA if in doubt.
2. Connect your laptop to the `Pepper` WiFi
    - SSID: **Pepper**
    - Password: **60169283**

### Turning on Pepper
1. Ensure the network router has been plugged in. Ask a teacher or TA if in doubt.
2. Press the start button on the stomach behind the tablet once quickly.
3. Light should come on in both eyes and shoulders.

### Getting Pepper IP address
1. Ensure Pepper is on and standing straight up
2. Press the button on the stomach behind the tablet once quickly
3. Pepper should say its IP address out loud.

### Connecting to Pepper
1. Ensure your laptop is connected to the `Pepper` network
2. Use either the [robot/robot_client.py](robot/robot_client.py) or [client.py](client.py) to test the connection. Examples:
    - [robot/robot_client.py](robot/robot_client.py): `python3 robot/robot_client.py INSERT_PEPPER_IP`
    - [client.py](client.py): `java -jar server.jar -g -s 300 -c "python3 client.py robot --ip INSERT_PEPPER_IP" -l levels/MAsimplegoalrecognition.lvl`

**Troubleshooting:**  
- Running into the exception: **Robot's IP not in configuration file, please update the configuration file with the correct robot IP.**
    - It happens that the robots change IP, when this happens, update the IP of your robot in  [robot_config.json](robot/robot_config.json) based on the robots ID.

### Putting Pepper to sleep/hibernate
1. Press the button on the stomach behind the tablet **twice quickly**.
2. Pepper should transition to its safe sleeping pose, cooling the motors and saving power.

### Turning Pepper off
1. Press and hold the the button on the stomach behind the tablet, till Pepper says *"Gnuk Gnuk"*.
2. Pepper should now go into the sleeping position and turn off all lights.

### Localization
You may observe that the robot's navigational accuracy as slightly lacking. It's also very sensitive to its starting position within the cells. These inaccuracies can accumulate and potentially cause frustration. By utilizing the [robot/robot_utils.py::VisionStreamThread](robot/robot_utils.py) class you can obtain data on the nearest apriltag visible to the robot (specifically via the camera located below the mouth). This information can be used to implement a basic controller by completing the `localization_controller(video_thread: VideoStreamThread)` method in the [robot/robot_client.py::RobotClient](robot/robot_client.py) class.  
Remember that `localization_controller(video_thread: VideoStreamThread)` must utilize an active `VisionStreamThread` as a parameter, which you can assign by using the `instantiate_vision_processes` function (refer to the
\_\_main\_\_ script in [robot/robot_client.py](robot/robot_client.py) for further details).  

A solution might be to develop a controller that begins by aligning the robot to the closest apriltag, followed by ensuring the correct orientation through a continual loop (you may need to specify an epsilon for both centering and orientation to help determine completion). Immediately after every $n$ actions in the action plan, you can call the controller to help mitigate the cumulative error. One thing you may discover is that certain actions cause more substantial errors than others. This could be an important factor to consider when deciding the point to activate the controller during the execution of a plan.

### Whisper Speech Recognition
We'll use OpenAI's Whisper for speech recognition because it works well in noisy situations.  
To set up Whisper, follow the guide here (read carefully): https://github.com/openai/whisper  
Although Whisper handles noise well, stand near your robot when talking. The first time you use Whisper, loading the base model may take a while. This only happens once per session.   
Here's a code example from the demo that transcribes a temporary `test.wav` file in the `tmp` folder (this is where the robot.listen() function from [robot/robot_client.py](robot/robot_client.py) will save to):
```python
# %% Imports
import whisper

# %% Transcription helper
def transcribe(audio_file: str, model: whisper.Whisper, language: str = "en") -> str:
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    result = whisper.transcribe(model, audio, fp16 = False, language=language)
    return result['text']

# %% Load model
# The list of available models can be found here: https://github.com/openai/whisper
model = whisper.load_model(
    name="small.en",
    download_root="tmp/whisper_models" # Ensures model weights are kept between container rebuilds
)

# %% Record audio
robot.listen(5)

# %% Transcribe audio file
audio_file = "tmp/test.wav"
transcription = transcribe(audio_file, model)
transcription
```

### Adding new functionality
If you'd like to try new things and add more features to the robot client, go ahead. You can find the complete NAOqi API proxies here: http://doc.aldebaran.com/2-5/naoqi/index.html.  
You can also include other features not in the API. To do this easily, follow the general procedure in [robot/robot_client.py](robot/robot_client.py).  
If you have interesting ideas, but are unsure if they can work, ask the Robot TA for help.