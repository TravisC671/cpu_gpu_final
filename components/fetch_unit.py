from components.system import System
from components.decoder import decode_instruction, Control


class Fetch_unit:
    def __init__(self, system: System):
        self._system = system
        pass

    def read_instr(self, address: int) -> Control:
        instruction = self._system.fetch_memory(address)
        return decode_instruction(instruction, self._system)
