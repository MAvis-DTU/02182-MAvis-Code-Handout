# Mavis: Searchclient

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
rm -rf 02182-MAvis-Code-Handout.git
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

The server requires at least a JRE for Java 11, and has been tested with OpenJDK.

The Python searchclient has been tested with Python 3.9, but should work with versions of Python above 3.7.
The searchclient requires the 'psutil' package to monitor its memory usage; the package can be installed with pip:
```shell
pip install psutil
```

## Usage

All the following commands assume the working directory is the one this readme is located in.

You can read about the server options using the -h argument:
```shell
java -jar server.jar -h
```

Starting the server using the searchclient:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python searchclient/searchclient.py" -l levels/SAD1.lvl
```

The searchclient uses the BFS search strategy by default. Use arguments -dfs, -astar, or -greedy to set
alternative search strategies (after you implement them). For instance, to use DFS search on the same level as above:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python searchclient/searchclient.py -dfs" -l levels/SAD1.lvl
```

When using either -astar or -greedy, you must also specify which heuristic to use. Use arguments -goalcount or
-advancedheuristic to select between the two heuristic in domains/hospital/heuristics.py.
For instance, to use A* search with a goal count heuristic, on the same level as above:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python searchclient/searchclient.py -astar -goalcount" -l levels/SAD1.lvl
```

## Debugging

As communication with the java server is performed over stdout, `print(<something>)` does not work directly. 
To get information sent to the terminal, you should use

    print(<something>, file=sys.stderr)

Note that the HospitalState has a nice string representation such that you can print states to the terminal 
by writing

    print(state, file=sys.stderr)

For more advanced debugging using your IDE, see the document debugging.pdf.

## Memory settings
*Unless your hardware is unable to support this, you should let the searchclient allocate at least 4GB of memory.*

The searchclient monitors its own process' memory usage and terminates the search if it exceeds a given number of MiB.

To set the max memory usage to 4GB:
```shell
java -jar server.jar -g -s 300 -t 180 -c "python searchclient/searchclient.py --max-memory 4g" -l levels/SAD1.lvl
```
Avoid setting max memory usage too high, since it will lead to your OS doing memory swapping which is terribly slow.
