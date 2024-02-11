from typing import Any
from collections import namedtuple
import re

class IndexedFile:
    class __IndexedPosition(namedtuple('IdxedPos', "pos idx")):
        def __str__(self) -> str:
            return self.pos.__str__()
        
        def __int__(self) -> int:
            return self.pos
        
        def __lt__(self, __value) -> bool:
            return self.pos < int(__value)
        
        def __gt__(self, __value) -> bool:
            return self.pos > int(__value)

        def __le__(self, __value) -> bool:
            return self.pos <= int(__value)
        
        def __ge__(self, __value) -> bool:
            return self.pos >= int(__value)

        def __eq__(self, __value) -> bool:
            return self.pos == int(__value)

        def __ne__(self, __value) -> bool:
            return self.pos != int(__value)
        
        def __hash__(self) -> int:
            return self.pos.__hash__()

    def __init__(self, path: str, *args):
        self.f = open(path, *args)
        self.cur_idx = 0
    
    def __enter__(self):
        self.f.__enter__()
        return self
    
    def __exit__(self, type, value, trace):
        self.f.__exit__(type, value, trace)
    
    def __iter__(self):
        return self.f.__iter__()

    def __next__(self):
        line = self.f.__next__()
        if line:
            self.cur_idx = self.cur_idx + 1
        return line
    
    def __getattr__(self, __name: str) -> Any:
        return self.f.__getattribute__(__name)
    
    def read(self, size: int) -> str:
        bytes = self.f.read(size)
        self.cur_idx = self.cur_idx + bytes.count('\n')
        return bytes

    def readline(self) -> str:
        line = self.f.readline()
        if line:
            self.cur_idx = self.cur_idx + 1
        return line
    
    def readlines(self) -> list:
        lines = self.f.readlines()
        self.cur_idx = len(lines)
        return lines
    
    def tell(self) -> __IndexedPosition:
        return self.__IndexedPosition(self.f.tell(), self.cur_idx)
    
    def seek(self, idxed_pos: __IndexedPosition) -> int:
        ret = self.f.seek(idxed_pos.pos)
        if ret != -1:
            self.cur_idx = idxed_pos.idx
        return ret
    
def openIndexedFile(path):
    return IndexedFile(path)

rb_extractor = re.compile(r'\((.*)\)')
sb_extractor = re.compile(r'\[(.*)\]')

def extArgsInRdBrac(expr: str) -> list:
    return re.findall(rb_extractor, expr)[0].split(',')

def extArgsInSqBrac(expr: str) -> list:
    return re.findall(sb_extractor, expr)[0].split(',')

if __name__ == "__main__":
    a = IndexedFile._IndexedFile__IndexedPosition(1, 2)
    b = IndexedFile._IndexedFile__IndexedPosition(5, 3)
    with openIndexedFile('test.m') as f:
        line = f.readline()
        while line:
            print(line.strip())
            line = f.readline()