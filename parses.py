#!/usr/bin/env python3

from pprint import pprint
import configparser
# from typing import Dictionary
import sys

#### MAZES FOR PROGRAMMERS

spaces = [' ', '\t', '\n']
settings = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 
            'OUTPUT_FILE', 'PERFECT', 'SEED']


class Config:
    def __init__(self):
        self.__params = {}

    def validate(self, filename: str) -> None:
        # try and except block and validate for neg. values
        with open(filename, 'rt') as file:
            for line in file:
                if line.strip()[0] != '#':
                    for s in spaces:
                        line = line.replace(s, '')
                    element = line.split('=')

                    if element[0] not in settings:
                        print(f"unknown: {element[0]}")
                    else:
                        self.__params[element[0]] = element[1]

            _entry = self.__params['ENTRY'].split(',')
            _exit = self.__params['EXIT'].split(',')
            

            self._width = int(self.__params['WIDTH'])
            self._height = int(self.__params['HEIGHT'])
            self._entry = ((int(_entry[0]), int(_entry[1]))) 
            self._exit = ((int(_exit[0]), int(_exit[0])))
            self._output_file = str(self.__params['OUTPUT_FILE'])
            self._perfect = bool(self.__params['PERFECT'])
            self._seed = int(self.__params['SEED'])

c = Config()
c.validate("config")
print(c._width, c._height, c._entry, c._exit, c._output_file, c._perfect, c._seed)
