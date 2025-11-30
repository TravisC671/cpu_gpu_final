from components.fetch_unit import Fetch_unit
from components.system import System
from components.decoder import Control, AM


class Sequencer:
    def __init__(self, system: System):
        self._system = system
        self._fetch_unit = Fetch_unit(system)
        self._pc = 0
        pass

    def start(self):
        self._pc = self._system.get_start_addr()
        halt_reason: str = ""
        print(" IC     IR    INST  MAR    AC-reg  Index Registers")
        while True:
            control = self._fetch_unit.read_instr(self._pc)
            instr_pc = self._pc
            self._pc += 1

            self._handle_instr(control)

            reg_str = self._system.get_registers()

            print(
                f"{instr_pc:0{3}X}:  {control.instr}  {control.instr_name:{4}}  {control.ea_str}  {reg_str}"
            )

            if control.instr_name == "HALT":
                halt_reason = "HALT intruction executed"
                break

            if control.instr_name == "????":
                halt_reason = "undefined opcode"
                break

            if control.am == AM.ILLEGAL:
                halt_reason = "illegal addressing mode"
                break

        print(f"Machine Halted - {halt_reason}")

    # acts as the alu, cant be moved since it would cause a circular dependacy
    # control is the data bus
    def _handle_instr(self, control: Control):

        match control.instr_name:
            case "HALT":
                return
            case "NOP":
                return
            case "LD":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator = value
                return
            case "ST":
                pass
            case "EM":
                pass
            case "LDX":
                pass
            case "STX":
                pass
            case "EMX":
                pass
            case "ADD":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator += value
                return
            case "SUB":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator -= value
                return
            case "CLR":
                pass
            case "COM":
                pass
            case "AND":
                pass
            case "OR":
                pass
            case "XOR":
                pass
            case "ADDX":
                pass
            case "SUBX":
                pass
            case "CLRX":
                pass
            case "J":
                if control.am == AM.IMMEDIATE:
                    #! Throw an error
                    return
                self._pc = control.ea
                return
            case "JZ":
                pass
            case "JN":
                pass
            case "JP":
                pass
