from rich.prompt import Prompt, FloatPrompt
from rich.console import Console
from rich.markdown import Markdown

from LittleManComputer import LittleManComputer
import Exceptions

console = Console()

try:
    console.print(Markdown("# Little Man Computer simulator"))
    computer = LittleManComputer(console)
    filename = Prompt.ask("Enter the filename of the program")
    computer.load(filename)
    clock = FloatPrompt.ask("Enter the clock speed (instructions/s)")
    if clock > 0:
        computer.clock = clock
    computer.run()

except Exceptions.UnknownVariable as e:
    console.log(f'Unknown variable at line {e.location + 1}', style='red')

except Exceptions.UnknownInstruction as e:
    console.log(f'Unknown instruction at line {e.location + 1}', style='red')

except Exceptions.UnknownLocation as e:
    console.log(f'Unknown branch location at line {e.location + 1}', style='red')

except Exceptions.UnlabeledDAT as e:
    console.log(f'Unlabeled DAT instruction at line {e.location + 1}', style='red')

except FileNotFoundError:
    console.log(f'File not found!', style='red')

