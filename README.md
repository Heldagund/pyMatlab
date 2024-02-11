# pyMatlab
pyMatlab is an external Matlab terminal and debugger using MATLAB Engine API for Python (under development)

It is developped based on the VSCode extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)
  
In case of copyright infringement, please contact sentinel.hdgd@gmail.com

## Requirements
Same requirements as the extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)

N.B. This project is developped using Python 3.8.10

## How to launch the terminal
1. First of all, make sure you are able to run the VSCode extension [Matlab Interactive Terminal](https://github.com/apommel/vscode-matlab-interactive-terminal)
2. Run the script ml_terminal.py in this repository

## What's new
1. To run a MATLAB script, please specify its relative or absolute path, e.g. script_name.m if the script is in the working directory
2. Use -i or --interactive option to run a script interactively. In this mode, any input or pause command will be detected and treated properly
3. Use -d or --debug option to debug a script. Add 'dbg' at the end of the line to set a breakpoint.
4. In the debug mode,
    - use 'step' to step to the next line;
    - use 'continue' to resume the execution;
    - use 'watch' to examine all variables in the workspace and their values;
    - use 'exit' to exit the program

## Restrictions
1. The intepreter is dumb. Any keyword (if, for, switch, end...) is only recognized at the beginning of the line
2. Step in and step out are currently unsupported
3. Encoding issues may happen for non ASCII caracters under the interactive and debug mode, e.g. figure title