from LittleManComputer import LittleManComputer, ProgramParser

computer = LittleManComputer()

parser = ProgramParser('program.txt')

computer.load(parser.parse())
computer.run()
# comp = LittleManComputer()
#
# comp.load(['901', '336', '733', '238', '339', '337', '536', '340', '539', '730',
#            '238', '730', '536', '140', '336', '537', '238', '337', '238', '721',
#            '608', '536', '340', '539', '238', '339', '337', '238', '730', '608',
#            '536', '902', '000', '538', '902', '000', '0', '0', '1', '0'])
#
#
# comp.run()
