# pyMatlab
External Matlab terminal and debugger using MATLAB Engine API for Python (under development)

Developped based on the VSCode extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)
  
In case of any copyright infringement, please contact sentinel.hdgd@gmail.com

## Requirements
Same requirements as the extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)

N.B. This project is developped using Python 3.8.10

## How to launch the terminal
1. First of all, make sure you are able to run the VSCode extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)
2. Run the script ml_terminal.py in this repository

## What's new
1. To run a MATLAB script, please specify its relative or absolute path (e.g. script_name.m if the script is in the working directory)
2. Use -i or --interactive option to run a script interactively. In this mode, any input or pause command will be detected and treated properly
3. Add 'dbg' at the end of the line to set a breakpoint. In the interactive mode, the excution will be suspended upon reaching this line and then it enters the debug mode
4. In the debug mode,
   - use 'step' to step to the next line;
   - use 'continue' to resume the execution;
   - use 'watch' to examine all variables in the workspace and their values;
   - use 'exit' to exit the program

## Restrictions
Do not define functions in the script. The core is currently unable to deal with it.
