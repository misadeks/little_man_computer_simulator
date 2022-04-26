import re

import Exceptions


class LittleManComputer:
    def __init__(self):
        self.memory = ['0'] * 100
        self.accumulator = 0
        self.programCounter = 0
        self.running = False

    def load(self, instructions):
        for idx, instruction in enumerate(instructions):
            self.memory[idx] = instruction

    def run(self):
        self.running = True
        while self.running:
            self.__instruction_parser__(self.memory[self.programCounter])

    def __reset__(self):
        self.running = False
        self.programCounter = 0

    def __instruction_parser__(self, instruction: str):
        if len(instruction) != 3:
            raise RuntimeError(f'Not an instruction! Memory location {self.programCounter}')

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
                    raise RuntimeError(f'Unknown instruction! Memory location {self.programCounter}')

            # hlt
            case '0':
                if instruction == '000':
                    self.__instruction_hlt__()
                else:
                    raise RuntimeError(f'Unknown instruction! Memory location {self.programCounter}')

    def __instruction__add__(self, data: str):
        self.programCounter += 1
        self.accumulator += int(self.memory[int(data)])

    def __instruction_sub__(self, data: str):
        self.programCounter += 1
        self.accumulator -= int(self.memory[int(data)])

    def __instruction_sta__(self, data: str):
        self.programCounter += 1
        self.memory[int(data)] = str(self.accumulator)

    def __instruction_lda__(self, data: str):
        self.programCounter += 1
        self.accumulator = int(self.memory[int(data)])

    def __instruction_bra__(self, data: str):
        self.programCounter += 1
        self.programCounter = int(data)

    def __instruction_brz__(self, data: str):
        self.programCounter += 1
        if self.accumulator == 0:
            self.programCounter = int(data)

    def __instruction_brp__(self, data: str):
        self.programCounter += 1
        if self.accumulator >= 0:
            self.programCounter = int(data)

    def __instruction_inp__(self):
        self.programCounter += 1
        self.accumulator = int(input())

    def __instruction_out__(self):
        self.programCounter += 1
        print(self.accumulator)

    def __instruction_hlt__(self):
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
        print(self.variables)
        compiled_program = []
        for instruction in self.program:
            compiled_program.append(self.parse_instruction(instruction))
        return compiled_program

    def __parse_dat_labels__(self):
        for idx, instruction in enumerate(self.program):
            instruction_match = re.match(self.instruction_pattern, instruction)
            if instruction_match and 'DAT' == instruction_match[2]:
                if instruction_match[1] == '':
                    raise Exceptions.UnlabeledDAT
                self.variables[instruction_match[1]] = \
                    [0, idx] if instruction_match[3] == '' else [instruction_match[3], idx]
            elif instruction_match and instruction_match[1] != '':
                self.labels[instruction_match[1]] = idx

    def parse_instruction(self, instruction):
        instruction_match = re.match(self.instruction_pattern, instruction)
        if not instruction_match:
            raise Exception # unknown instruction or error
        location = instruction_match[3]

        try:
            match instruction_match[2]:
                case 'ADD':
                    return '1' + f'{self.variables[location][1]:02d}'
                case 'SUB':
                    return '2' + f'{self.variables[location][1]:02d}'
                case 'STA':
                    return '3' + f'{self.variables[location][1]:02d}'
                case 'LDA':
                    return '5' + f'{self.variables[location][1]:02d}'
                case 'BRA':
                    return '6' + f'{self.labels[location]:02d}'
                case 'BRZ':
                    return '7' + f'{self.labels[location]:02d}'
                case 'BRP':
                    return '8' + f'{self.labels[location]:02d}'
                case 'INP':
                    return '901'
                case 'OUT':
                    return '902'
                case 'HLT':
                    return '000'
                case 'DAT':
                    return f'{self.variables[instruction_match[1]][0]}'
                case _:
                    raise Exception # error
        except KeyError:
            raise Exception # unknown or missing variable


        # if 'INP' in instruction:
        #     return '901'
        # elif 'OUT' in instruction:
        #     return '902'
        # elif 'LDA' in instruction:
        #     location = instruction[instruction.index('LDA') + 1]
        #     return '5' + str(self.variables[location][1])
        # elif 'STA' in instruction:
        #     pass
        # elif 'ADD' in instruction:
        #     pass
        # elif 'SUB' in instruction:
        #     pass
        # elif 'BRP' in instruction:
        #     pass
        # elif 'BRZ' in instruction:
        #     pass
        # elif 'BRA' in instruction:
        #     pass
        # elif 'HLT' in instruction:
        #     pass
        # elif 'DAT' in instruction:
        #     pass
        # else:
        #     # unknown instruction
        #     raise Exception
