import re
import time
import asyncio

import rich
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.prompt import IntPrompt
from rich.table import Table
from rich.console import Console
from rich.text import Text

import Exceptions


def generate_table(memory, program_counter):
    table = Table(show_header=False, show_lines=True)
    for col in range(0, 10):
        table.add_column()
    # for m in [memory[i:i + 10] for i in range(0, len(memory), 10)]:
    #     table.add_row(*m)

    current_row = []
    rows = []
    added = 0
    for idx, mem in enumerate(memory):
        text = Text(mem, style='bold red') if idx == program_counter else mem
        if added < 10:
            current_row.append(text)
        else:
            rows.append(current_row)
            current_row = []
            current_row.append(text)
            added = 0
        added += 1

    for r in rows:
        table.add_row(*r)

    return table


class LittleManComputer:
    def __init__(self, console: rich.console, clock=None):
        self.memory = ['0'] * 100
        self.accumulator = 0
        self.program_counter = 0
        self.running = False
        self.console = console
        self.clock = clock if clock is not None else 0
        self.output = []
        self.program = ''

    def load(self, filename):
        self.load_memory(ProgramParser(filename).parse())
        with(open(filename)) as file:
            self.program = file.read()

    def load_memory(self, instructions):
        for idx, instruction in enumerate(instructions):
            self.memory[idx] = instruction

    def ui(self):
        screen = Table(show_header=True)
        screen.add_column('Program')
        screen.add_column('Memory')
        screen.add_column('Parameters')
        screen.add_column('Output')

        output_text = '\n'.join(self.output)
        parameters_text = f'Accumulator = {self.accumulator}\n' \
                          f'Program Counter = {self.program_counter}\n' \
                          f'Clock = {self.clock} ins/s\n\n' \
                          f'Current Instruction '
        screen.add_row(Text(self.program), generate_table(self.memory, self.program_counter),
                       Text(parameters_text, style='green'), Text(output_text, style='cyan'))

        return screen

    def run(self):
        self.console.print('Program started!', style='green')
        self.running = True
        while self.running:
            self.console.clear()

            if self.clock <= 5 and self.clock != 0 and self.memory[self.program_counter] != '000':
                self.console.print(self.ui())

            self.__instruction_parser__(self.memory[self.program_counter])

            if self.clock != 0:
                time.sleep(1/self.clock)
        self.console.print('Program halted!', style='green')

    def __reset__(self):
        self.running = False
        self.program_counter = 0

    def __instruction_parser__(self, instruction: str):
        if len(instruction) != 3:
            raise RuntimeError(f'Not an instruction! Memory location {self.program_counter}')

        instruction_code = instruction[0]
        match instruction_code:
            # add
            case '1':
                self.__instruction__add__(instruction[1:3])

            # sub
            case '2':
                self.__instruction_sub__(instruction[1:3])

            # sta
            case '3':
                self.__instruction_sta__(instruction[1:3])

            # lda
            case '5':
                self.__instruction_lda__(instruction[1:3])

            # bra
            case '6':
                self.__instruction_bra__(instruction[1:3])

            # brz
            case '7':
                self.__instruction_brz__(instruction[1:3])

            # brp
            case '8':
                self.__instruction_brp__(instruction[1:3])

            # inp/out
            case '9':
                if instruction == '901':
                    self.__instruction_inp__()
                elif instruction == '902':
                    self.__instruction_out__()
                else:
                    raise Exceptions.UnknownInstruction(self.program_counter)

            # hlt
            case '0':
                if instruction == '000':
                    self.__instruction_hlt__()
                else:
                    raise Exceptions.UnknownInstruction(self.program_counter)

    def __instruction__add__(self, data: str):
        self.program_counter += 1
        self.accumulator += int(self.memory[int(data)])

    def __instruction_sub__(self, data: str):
        self.program_counter += 1
        self.accumulator -= int(self.memory[int(data)])

    def __instruction_sta__(self, data: str):
        self.program_counter += 1
        self.memory[int(data)] = str(self.accumulator)

    def __instruction_lda__(self, data: str):
        self.program_counter += 1
        self.accumulator = int(self.memory[int(data)])

    def __instruction_bra__(self, data: str):
        self.program_counter += 1
        self.program_counter = int(data)

    def __instruction_brz__(self, data: str):
        self.program_counter += 1
        if self.accumulator == 0:
            self.program_counter = int(data)

    def __instruction_brp__(self, data: str):
        self.program_counter += 1
        if self.accumulator >= 0:
            self.program_counter = int(data)

    def __instruction_inp__(self):
        self.program_counter += 1
        self.accumulator = IntPrompt.ask("Input a number")

    def __instruction_out__(self):
        self.program_counter += 1
        self.output.append(str(self.accumulator))

    def __instruction_hlt__(self):
        self.console.clear()
        self.console.print(self.ui())
        self.__reset__()


class ProgramParser:
    instruction_names = ['INP', 'OUT', 'LDA', 'STA', 'ADD', 'SUB', 'BRP', 'BRZ', 'BRA', 'HLT', 'DAT']

    def __init__(self, program_filename):
        self.instruction_pattern = r'^(\w*)\s*(INP|OUT|LDA|STA|ADD|SUB|BRP|BRZ|BRA|HLT|DAT)\s*([a-zA-Z0-9]*)$'
        self.program = []
        with open(program_filename) as file:
            for line in file:
                if line != '\n':
                    self.program.append(line)
        self.variables = {}
        self.labels = {}


    def parse(self):
        self.__parse_dat_labels__()
        compiled_program = []
        for idx, instruction in enumerate(self.program):
            compiled_program.append(self.parse_instruction(instruction, idx))
        return compiled_program

    def __parse_dat_labels__(self):
        for idx, instruction in enumerate(self.program):
            instruction_match = re.match(self.instruction_pattern, instruction)
            if instruction_match and 'DAT' == instruction_match[2]:
                if instruction_match[1] == '':
                    raise Exceptions.UnlabeledDAT(idx)
                self.variables[instruction_match[1]] = \
                    [0, idx] if instruction_match[3] == '' else [instruction_match[3], idx]
            elif instruction_match and instruction_match[1] != '':
                self.labels[instruction_match[1]] = idx

    def parse_instruction(self, instruction, idx):
        instruction_match = re.match(self.instruction_pattern, instruction)
        if not instruction_match:
            raise Exceptions.UnknownInstruction(idx)
        location = instruction_match[3]

        match instruction_match[2]:
            case 'ADD':
                try:
                    return '1' + f'{self.variables[location][1]:02d}'
                except KeyError:
                    raise Exceptions.UnknownVariable(idx)
            case 'SUB':
                try:
                    return '2' + f'{self.variables[location][1]:02d}'
                except KeyError:
                    raise Exceptions.UnknownVariable(idx)
            case 'STA':
                try:
                    return '3' + f'{self.variables[location][1]:02d}'
                except KeyError:
                    raise Exceptions.UnknownVariable(idx)
            case 'LDA':
                try:
                    return '5' + f'{self.variables[location][1]:02d}'
                except KeyError:
                    raise Exceptions.UnknownVariable(idx)
            case 'BRA':
                try:
                    return '6' + f'{self.labels[location]:02d}'
                except KeyError:
                    raise Exceptions.UnknownLocation(idx)
            case 'BRZ':
                try:
                    return '7' + f'{self.labels[location]:02d}'
                except KeyError:
                    raise Exceptions.UnknownLocation
            case 'BRP':
                try:
                    return '8' + f'{self.labels[location]:02d}'
                except KeyError:
                    raise Exceptions.UnknownLocation(idx)
            case 'INP':
                return '901'
            case 'OUT':
                return '902'
            case 'HLT':
                return '000'
            case 'DAT':
                return f'{self.variables[instruction_match[1]][0]}'
            case _:
                raise Exceptions.UnknownInstruction(idx)
