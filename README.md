# Mavis: Client

This readme describes how to use the included Python search client with the server that is contained in server.jar.

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

The Python searchclient has been tested with Python 3.9, but should work with versions of Python above 3.7.
The searchclient requires the pip packages outlined in the [Devcontainer](#devcontainer) section.

To interact with the Pepper robots its python SDK, which is currently only python2 compatible, has to be installed. A guide to setup the SDK can be found in [PepperSetupGuide](./docs/PepperSetupGuide.pdf).

## Devcontainer
To simplify the setup and installation of required dependencies, a [devcontainer](https://containers.dev/overview) has been created. This [docker](https://www.docker.com/) based development environment ensures you have all the necessary dependencies installed, and that your groups environment is the same, thus avoiding the "It works on my computer" cliché.

The environment comes preconfigured with:
- **Java (OpenJDK 17)** – Access via `java`
- **Python 3.12** (for the client) – Access via `python3` - with the following pip dependencies, specified in [requirements.searchclient.txt](.devcontainer/requirements.searchclient.txt)
    - `psutil` to monitor its memory usage.
    - `debugpy` required to allow debugging through the java server
    - `msgpack` to facilitate communication between the robot server and the client
    - `numpy` to facilitate communication between the robot server and the client
    - Non-required packages:
        - `opencv-python` intended for manipulating image data from the robots
        - `pupil-apriltags` required to process apriltags
        - `graphviz` required to visualize solution graphs
- **Python 2.7** (for the robot server) – Access via `python2` - with the following pip dependencies, specified in [requirements.robotserver.txt](.devcontainer/requirements.robotserver.txt)
    - `scp` to facilitate communication between the robot server and the actual robot
    - `msgpack` to facilitate communication between the robot server and the client
- **Naoqi SDK (Pepper Robot Python SDK)** – Can be imported in Python 2 (`import naoqi`)

### Setup
To setup the devcontainer the following **prerequisites** need to be installed:
1. [Docker](https://www.docker.com/)
    - **Note:** If you're using Windows, you may need to enable WSL2 and ensure your user has the correct Docker permissions.
2. [Visual studio code](https://code.visualstudio.com/)
3. The [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) vscode extension.
4. You have followed the [Private repository setup](#private-repository-setup)

With the prerequisites installed, follow these steps:
1. Open your repository in vscode
2. **ONLY FOR MAC AND ARCH:** Replace the Windows/Debian configuration with the Mac/Arch configuration in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
2. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
3. Run the `Dev Containers: Rebuild and Reopen in Container` command
    - The first build may take a while - check the logs to track progress.
    - Once your files appear in the Explorer (left panel), the devcontainer is ready.

**FOR MAC AND ARCH:** Due to inefficient native graphics forwarding, Mac and Arch-based systems cannot efficiently run the server graphics natively. As a workaround [noVNC](https://novnc.com/info.html) have been used to forward the graphics via a webserver.    
So to see the virtual environment, open [localhost:8080/vnc.html](http://localhost:8080/vnc.html) and press connect.  

### Tips & Troubleshooting
#### Selecting python interpreter
As the client and the server uses different python versions, selecting the version you intend to use to run the code provides accurate [IntelliSense](https://code.visualstudio.com/docs/editor/intellisense), and ensures the right version is used if running it directly from vscode (`F5`).  
**Steps:**
1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
2. Run the `Python: Select Interpreter` command
3. Select the appropriate python version

### Adding pip packages
To ensure packages are installed when building or rebuilding the devcontainer, add wanted pip packages to the [.devcontainer/requirements.searchclient.txt](.devcontainer/requirements.searchclient.txt) file and rebuild the container (vscode command `Dev Containers: Rebuild Container`).

### (Mac/Arch) changing the resolution of the virtual environment
1. Open [.devcontainer/docker-compose.yml](.devcontainer/docker-compose.yml)
2. Adjust the `DISPLAY_WIDTH` and `DISPLAY_HEIGHT` environment variables to your preference
3. Rebuild the devcontainer
    1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
    2. Run the `Dev Containers: Rebuild Container` command

### X11 Problems
1. Follow the Mac/Arch (noVNC) setup steps. Updating the [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
2. Rebuild the devcontainer
    1. Open the vscode command palette (`ctrl+shift+p` or `cmd+shift+p`)
    2. Run the `Dev Containers: Rebuild Container` command
3. Access the GUI on [localhost:8080/vnc.html](http://localhost:8080/vnc.html)

## Usage

All the following commands assume the working directory is the one this readme is located in.

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

## Debugging
As communication with the java server is performed over stdout, `print(<something>)` does not work directly. 
To get information sent to the terminal, you should use

    print(<something>, file=sys.stderr)

Note that the HospitalState has a nice string representation such that you can print states to the terminal 
by writing

    print(state, file=sys.stderr)

For more advanced debugging using vscode and the devcontainer, simply add the `--debug` flag when running the server, e.g.:
```shell
java -jar server.jar -g -c "python3 client.py --debug classic" -l levels/SAD1.lvl
```
**Note that the server will still timeout if the `-t` argument is given.**

## Memory settings
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

## Router Connection Information for robots 
Name:     **Pepper**  
Password: **60169283**
