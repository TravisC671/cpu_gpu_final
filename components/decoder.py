from dataclasses import dataclass
from typing import List
from enum import Enum
from components.system import Register, System


# Addressing mode
class AM(Enum):
    DIRECT = 0
    IMMEDIATE = 1
    INDEXED = 2
    INDIRECT = 3
    INDEXED_INDIRECT = 4
    ILLEGAL = 5


AM_LOOKUP = {
    0b0000: AM.DIRECT,
    0b0001: AM.IMMEDIATE,
    0b0010: AM.INDEXED,
    0b0100: AM.INDIRECT,
    0b0110: AM.INDEXED_INDIRECT,
}


@dataclass
class Control:
    instr_name: str
    instr: str
    am: AM
    ea_str: str
    ea: int


# fmt: off
INSTRUCTION_TABLE: List[List[None | str]] = [
#    00   , 01   , 10    , 11
    ["HALT", "LD" , "ADD" , "J" ],  # 0000
    ["NOP" , "ST" , "SUB" , "JZ"],  # 0001
    [ None , "EM" , "CLR" , "JN"],  # 0010
    [ None , None , "COM" , "JP"],  # 0011
    [ None , None , "AND" , None],  # 0100
    [ None , None , "OR"  , None],  # 0101
    [ None , None , "XOR" , None],  # 0110
    [ None , None , None  , None],  # 0111
    [ None , "LDX", "ADDX", None],  # 1000
    [ None , "STX", "SUBX", None],  # 1001
    [ None , "EMX", "CLRX", None],  # 1010
    [ None , None , None  , None],  # 1011
    [ None , None , None  , None],  # 1100
    [ None , None , None  , None],  # 1101
    [ None , None , None  , None],  # 1110
    [ None , None , None  , None],  # 1111
]
# fmt: on


def decode_instruction(instruction: str, system: System) -> Control:
    bin_instr = f"{int(instruction, 16):0{24}b}"

    category = int(bin_instr[-12:-10], 2)
    operation = int(bin_instr[-10:-6], 2)

    # technically this isn't the opcode but I'm running out of names
    opcode = INSTRUCTION_TABLE[operation][category]

    instr_name = opcode or "????"

    addressing_mode = int(bin_instr[-6:-2])

    am = AM_LOOKUP.get(addressing_mode, AM.ILLEGAL)

    ea_str = instruction[:3]
    if am == AM.IMMEDIATE:
        ea_str = "IMM"
    elif category == 0 or not opcode:
        ea_str = "   "
    elif am == AM.ILLEGAL:
        ea_str = "???"

    ea = 0

    match am:
        case AM.DIRECT:
            ea = int(instruction[:3], 16)

        case AM.IMMEDIATE:
            #! do I need to sign extend if its already 12 bits???
            ea = int(instruction[:3], 16)

        case AM.INDEXED:
            reg = Register(int(bin_instr[-2:0]) + 1)
            value = system.get_register(reg)
            ea = (int(instruction[:3], 16) + value) % 4095

        case AM.INDIRECT:
            value = system.fetch_memory(int(instruction[:3], 16))
            ea = (int(value) >> 12) % 4095

        case AM.INDEXED_INDIRECT:
            # perform indexing
            reg = Register(int(bin_instr[-2:0]) + 1)
            value = system.get_register(reg)
            addr = (int(instruction[:3], 16) + value) % 4095

            # get value from the data at the memory position
            indirect_value = system.fetch_memory(addr)
            ea = (int(indirect_value) >> 12) % 4095

    return Control(instr_name, instruction, am, ea_str, ea)


def sign_extend(input: str, target_len: int) -> int:
    sign = input[0]

    while len(input) < target_len:
        input = sign + input

    return int(input)
