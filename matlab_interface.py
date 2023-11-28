# Developed by Aurelien Pommel and other contributors

# Trying to have a basic Python 2 compatibility
from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass

import os
from io import StringIO
from textwrap import dedent
import argparse
from time import sleep
import re
# import sys

global import_fail
try: # Check if the Matlab Engine is installed
    import matlab.engine
    from matlab.engine import RejectedExecutionError as MatlabTerminated
except ImportError:
    print("MATLAB Engine for Python cannot be detected. Please install it for the extension to work.")
    import_fail = True
else:
    import_fail = False

# For lauch animation
frames = [
    "[ =    ]",
    "[  =   ]",
    "[   =  ]",
    "[    = ]",
    "[     =]",
    "[    = ]",
    "[   =  ]",
    "[  =   ]",
    "[ =    ]",
    "[=     ]",
]

# For running script (sr: script runner)
initiators = ['if', 'while', 'for', 'switch']
terminators = ['else', 'elseif', 'end', 'case', 'otherwise']
sr_parser = argparse.ArgumentParser()
sr_parser.add_argument("script", help="path of the script to run")
sr_parser.add_argument("-i", "--interactive", help="Activate this option if your script has pause",
                    action="store_true")

class MatlabInterface:
    global import_fail

    def __init__(self):
        # OS checks related work
        if os.name == 'nt':
            self.cls_str = 'cls'
        else:
            self.cls_str = 'clear'
        self.clear()

        if not import_fail:
            try:
                future = matlab.engine.start_matlab(background=True)
                print('Starting Matlab engine ', frames[-1], end = '', flush = True)
                while not future.done():
                    for i in range(len(frames)):
                        sleep(0.5)
                        print('\b\b\b\b\b\b\b\b{}'.format(frames[i]), end = '', flush = True)
                self.clear()
                self.eng = future.result()
                intro = '''\
                MATLAB Interactive Terminal (R{release})
                
                To get started, type one of these commands:
                    helpwin          Provide access to help comments for all functions
                    helpdesk         Open help browser
                    demo             Access product examples in Help browser
                
                For product information, visit https://www.mathworks.com.
                '''.format(release=self.release())
                print(dedent(intro))

            except Exception as e:
                self.clear()
                print("MATLAB Engine for Python exited prematurely.")
                print(e)
                # TODO: test if this line is necessary
                # sys.exit()

        else:
            print("Launching MATLAB failed: Error starting MATLAB process in MATLAB Engine for Python.")
    
    def __del__(self):
        if not import_fail:
            self.eng.quit()

    def clear(self):
        os.system(self.cls_str)

    def release(self):
        release_str = "version('-release');"
        res = self.eng.eval(release_str)
        return res

    def run_line(self, line: str, output = True):
        try:
            stream = StringIO()
            err_stream = StringIO()
            if output == True:
                self.eng.eval(line, nargout=0, stdout=stream, stderr=err_stream)
                return stream.getvalue()
            else:
                return self.eng.eval(line, nargout=1, stdout=stream, stderr=err_stream)
                
        except MatlabTerminated:
            print(stream.getvalue(), err_stream.getvalue(), sep="\n")
            print("MATLAB process terminated.")
            print("Restarting MATLAB Engine for Python...")
            self.eng = matlab.engine.start_matlab()
            print("Restarted MATLAB process.")

        except : # The other exceptions are handled by Matlab
            print(stream.getvalue(), err_stream.getvalue(), sep="\n")

    def run_script(self, script_path):
        if not import_fail:

            try:
                print("File: \"{}\"".format(script_path))
                stream = StringIO()
                err_stream = StringIO()
                self.eng.run(script_path, nargout=0, stdout=stream, stderr=err_stream)
                print(stream.getvalue())

            except MatlabTerminated:
                print(stream.getvalue(), err_stream.getvalue(), sep="\n")
                print("MATLAB process terminated.")
                print("Restarting MATLAB Engine for Python...")
                self.eng = matlab.engine.start_matlab()
                print("Restarted MATLAB process.")

            except : # The other exceptions are handled by Matlab
                print(stream.getvalue(), err_stream.getvalue(), sep="\n")

######################### Experimental feature #########################
    def process_input(self, line) -> bool:
        # No screen output with or without a semicolon following the command
        try:
            [name, expr] = line.split('=', 1)
        except ValueError:
            # The input value is not assigned to a variable (WHO WILL DO THIS!) 
            name = None
            expr = line

        # Extract input arguments
        p = re.compile(r'[(](.*)[)]') 
        args = re.findall(p, expr)[0].split(',')
        if not args:
            print('Not enough arguments for the input command')
            return False
        
        # Get the input via python
        prompt = eval(args[0])
        user_input = input(prompt)

        # Assign the input value to a variable
        if name:
            if len(args) > 1:
                if args[1].find('s') != -1:
                    self.run_line("assignin('base','{}','{}')".format(name.strip(), user_input))
                else:
                    print('Unrecognized argument{}'.format(args[1]))
                    return False
            else:
                self.run_line("assignin('base','{}',{})".format(name.strip(), user_input))
        return True

    def debug_loop(self, f) -> bool:
        while True:
            print('dbg >>> ', end = '')
            dbg_cmd = input().strip()
            if dbg_cmd == 'exit':
                return False
            if dbg_cmd == 'step':
                break
            if dbg_cmd == 'continue':
                self.debug_mode = False
                break
            if dbg_cmd == 'watch':
                vars = self.run_line('who', output = False)
                if vars:
                    for var in vars:
                        # To make the output more readable
                        print(self.run_line(var))
                        # print('{}: {}'.format(var, self.eng.workspace[var]))  
        return True
        
    def run_sequential(self, f) -> bool:
        line = f.readline()
        while line:
            line = line.strip()
            # empty line or comment
            if line == '' or line[0] == '%':
                line = f.readline()
                continue

            if self.debug_mode:
                print('Stop at line:\n    ', line)
                if not self.debug_loop(f):
                    return False
                line = line.replace('dbg', '')

            first_word = line.split()[0]
            if first_word == 'if':
                if not self.run_if_block(f, line.lstrip('if')):
                    print('Error occurred around line:\n    ', line)
                    return False
            elif first_word == 'while':
                if not self.run_while_block(f, line.lstrip('while')):
                    print('Error occurred around line:\n    ', line)
                    return False
            elif first_word == 'for':
                if not self.run_for_block(f, line.lstrip('for')):
                    print('Error occurred around line:\n    ', line)
                    return False
            elif first_word == 'switch':
                if not self.run_switch_block(f, line.lstrip('switch')):
                    print('Error occurred around line:\n    ', line)
                    return False
            elif first_word in terminators:
                break
            else:
                if line.endswith('dbg'):
                    self.debug_mode = True
                    continue

                elif line.find('input(') != -1:
                    if not self.process_input(line):
                        print('Error occurred around line:\n    ', f.readline())
                        return False

                elif line.find('pause') != -1 :
                    line = line.replace('pause', '')
                    output = self.run_line(line)
                    if output:
                        print(output)
                    input()

                else:
                    output = self.run_line(line)
                    if output:
                        print(output)
            line = f.readline()
        return True
    
    def get_keyword_pos(self, f, key: str, pos_max: int = -1) -> int:
        init_pos = f.tell()
        # if key == 'end' and init_pos in self.pos_cache:
        #     print('cache hit')
        #     return self.pos_cache[init_pos]
        found = False
        key_pos = init_pos
        line = f.readline()
        while line:
            if pos_max != -1 and key_pos >= pos_max:
                break
            try:
                first_word = line.lstrip().split()[0]
                if first_word in initiators:
                    key_pos = self.get_keyword_pos(f, 'end', pos_max)
                    if key_pos == -1:
                        print('Syntax error: the end of nested {} block is missing!'.format(first_word))
                        return -1
                    f.seek(key_pos)
                    f.readline()
                # 'elseif' is considered the same as 'else'
                elif first_word.startswith(key):
                    found = True
                    break
            except IndexError:
                # the line is empty
                pass
            key_pos = f.tell()
            line = f.readline()
        f.seek(init_pos)
        if found:
            # if key == 'end':
            #     print('cache store')
            #     self.pos_cache[init_pos] = key_pos
            return key_pos
        else:
            return -1
        
    def run_if_block(self, f, condition: str) -> bool:
        pos_end = self.get_keyword_pos(f, 'end')
        if pos_end == -1:
            print('Syntax error: the end of if block is missing!')
            return False
        if self.run_line(condition, output = False):
            # 1st case
            # if True
            #   statements
            # (
            # else/elseif xxx
            #   statements
            # )
            # end
            if not self.run_sequential(f):
                return False

            # go to the start of next block
            f.seek(pos_end)
            f.readline()
        else:
            pos_else = self.get_keyword_pos(f, 'else', pos_end)
            if pos_else == -1:
                # 2th case
                # if False
                #   statements
                # end
                f.seek(pos_end)
                f.readline()
            else:
                f.seek(pos_else)
                line = f.readline()
                if line.startswith('elseif'):
                    # 3nd case
                    # if False
                    #   statements
                    # elseif xxx
                    #   statements
                    # (
                    # else/elseif xxx
                    #   statements
                    # )
                    # end

                    # elseif statement can be regarded as if statement 
                    if not self.run_if_block(f, line.lstrip('elseif').strip()):
                        return False
                else:
                    # 4rd case
                    # if False
                    #   statements
                    # else
                    #   statements
                    # end
                    # The file pointer already points to the start of next
                    # block after the call of run_sequential
                    if not self.run_sequential(f):
                        return False
        return True
    
    def run_while_block(self, f, condition: str):
        pos_begin = f.tell()
        pos_end = self.get_keyword_pos(f, 'end')
        if pos_end == -1:
            print('Syntax error: the end of while block is missing!')
            return False

        while self.run_line(condition, output = False):
            if not self.run_sequential(f):
                return False
            f.seek(pos_begin)
        # Go to the start of next block
        f.seek(pos_end)
        f.readline()
        return True

    # TODO: support for vector loop variable
    def run_for_block(self, f, expr: str):
        def get_loop_variable(expr: str):
            [name, range_expr] = expr.split('=')
            range = self.run_line(range_expr.strip(), output = False)
            return {'name': name.strip(), 'range': range[0]}
        
        loop_var = get_loop_variable(expr)
        pos_begin = f.tell()
        pos_end = self.get_keyword_pos(f, 'end')
        if pos_end == -1:
            print('Syntax error: the end of for block is missing!')
            return False
        
        for i in loop_var['range']:
            self.eng.workspace[loop_var['name']] = i
            if not self.run_sequential(f):
                return False
            f.seek(pos_begin)
        # Go to the start of next block
        f.seek(pos_end)
        f.readline()
        return True

    def run_switch_block(self, f, swtich_expr) -> bool:
        def expr_match(swtich_expr, case_expr) -> bool:
            return self.run_line('{}=={}'.format(swtich_expr, case_expr), output = False)
        
        pos_end = self.get_keyword_pos(f, 'end')
        if pos_end == -1:
            print('Syntax error: the end of switch block is missing!')
            return False
        pos_otherwise = self.get_keyword_pos(f, 'otherwise', pos_end)
        done = False

        pos_case = self.get_keyword_pos(f, 'case', pos_end)
        if pos_case == -1:
            print('Syntax error: No case in switch block')
            return False
        while pos_case != -1:
            f.seek(pos_case)
            line = f.readline()
            case_expr = line.lstrip().lstrip('case').strip()
            if expr_match(swtich_expr, case_expr):
                if not self.run_sequential(f):
                    return False
                done = True
                break
            pos_case = self.get_keyword_pos(f, 'case', pos_end)

        if not done and pos_otherwise != -1:
            f.seek(pos_otherwise)
            line = f.readline()
            if not self.run_sequential(f):
                return False
        # Go to the start of next block
        f.seek(pos_end)
        f.readline()
        return True
    
    def run_interactive_script(self, script_path):
        if not import_fail:
            # Create a cache to store the pairs of the block initiator
            # position and their corresponding end position in the script
            # 
            # It is useful for nested blocks but not so necessary as we don't
            # usually create complexe structures when writing Matlab script
            # 
            # The cache action is done in get_keyword_pos
            # self.pos_cache = {}
            self.debug_mode = False
            print("File: \"{}\"".format(script_path))
            # Exexcute line by line
            try:
                with open(script_path) as s:
                    self.run_sequential(s)
            except FileNotFoundError:
                print("File is not found!")
            # Clear the cache
            # self.pos_cache.clear()

#######################################################################################

    # def run_selection(self, temp_path):
    #     if not import_fail:
    #         f = open(temp_path, 'r')
    #         print("Running:")

    #         try: # Print the content of the selection before running it, encoding issues can happen
    #             for line in f:
    #                 print(line, end='')

    #         except UnicodeDecodeError:
    #             print("current selection")

    #         print('\n')
    #         f.close()

    #         try:
    #             stream = StringIO()
    #             err_stream = StringIO()
    #             self.eng.run(temp_path, nargout=0, stdout=stream, stderr=err_stream)
    #             print(stream.getvalue())

    #         except MatlabTerminated:
    #             print(stream.getvalue(), err_stream.getvalue(), sep="\n")
    #             print("MATLAB terminated. Restarting the engine...")
    #             self.eng = matlab.engine.start_matlab()
    #             print("MATLAB restarted")

    #         except : # The other exceptions are handled by Matlab
    #             print(stream.getvalue(), err_stream.getvalue(), sep="\n")

    #         finally:
    #             os.remove(temp_path)
    #             os.rmdir(os.path.dirname(temp_path))

    def interactive_loop(self):
        loop=True # Looping allows for an interactive terminal
        # mode = InterfaceMode.COMMAND_WINDOW

        while loop and not import_fail:
            print('>>> ', end='')
            command = input().strip()
            cmd_tokens = command.split()

            # Input is empty
            if not cmd_tokens:
                continue
            
            if cmd_tokens[0]=="exit" or cmd_tokens[0]=="exit()": # Keywords to leave the engine
                loop=False

            elif cmd_tokens[0]=="clc" or cmd_tokens[0]=="clc()": # matlab terminal clearing must be reimplemented
                self.clear()

            else:
                if cmd_tokens[0].endswith('.m'):
                    # script runner mode
                    args = sr_parser.parse_args(command.split())
                    if args.interactive:
                        self.run_interactive_script(args.script)
                    else:
                        self.run_script(args.script)
                else:
                    # command window mode
                    output = self.run_line(command)
                    if output:
                        print(output)
