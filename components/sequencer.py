from components.fetch_unit import Fetch_unit
from components.system import System, Register
from components.decoder import Control, AM
from enum import Enum


class L_AM(Enum):
    Legal = (0,)
    Ignored = (1,)
    Illegal = 2


class Sequencer:
    def __init__(self, system: System):
        self._system = system
        self._fetch_unit = Fetch_unit(system)
        self._pc = 0
        pass

    def start(self):
        self._pc = self._system.get_start_addr()
        halt_reason: str = ""
        print(" IC     IR    INST  MAR    AC-reg     Index Registers")
        while True:
            control = self._fetch_unit.read_instr(self._pc)
            instr_pc = self._pc
            self._pc += 1

            mode_result = self._handle_instr(control)

            reg_str = self._system.get_registers()

            if mode_result == L_AM.Illegal:
                print(
                    f"{instr_pc:0{3}X}:  {control.instr}  {control.instr_name:{4}}  ???  {reg_str}"
                )
                halt_reason = "illegal addressing mode"
                break

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
    # returns if the instruction was legal or not
    def _handle_instr(self, control: Control) -> L_AM:

        match control.instr_name:
            case "HALT":
                return L_AM.Ignored
            case "NOP":
                return L_AM.Ignored
            case "LD":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator = value
                return L_AM.Legal
            case "ST":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal
                self._system.insert_memory(
                    control.ea, f"{self._system.accumulator:06x}"
                )
                return
            case "EM":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal

                temp_val = self._system.fetch_memory(control.ea)

                self._system.insert_memory(control.ea, self._system.accumulator)
                self._system.accumulator = temp_val

                return L_AM.Legal
            case "LDX":
                value: int = 0

                if control.am == AM.DIRECT:
                    value = int(self._system.fetch_memory(control.ea), 16)
                elif control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    return L_AM.Illegal

                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                self._system.set_register(reg, value >> 12)

                return L_AM.Legal
            case "STX":
                if control.am != AM.DIRECT:
                    return L_AM.Illegal

                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                value = self._system.get_register(reg) << 12

                self._system.insert_memory(control.ea, f"{value:0{24}b}")

                return L_AM.Legal
            case "EMX":
                if control.am != AM.DIRECT:
                    return L_AM.Illegal

                temp_value = int(self._system.fetch_memory(control.ea), 16)

                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                value = self._system.get_register(reg) << 12

                self._system.insert_memory(control.ea, f"{value:0{24}b}")

                self._system.set_register(reg, temp_value >> 12)

                return L_AM.Legal
            case "ADD":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator += value
                return L_AM.Legal
            case "SUB":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095
                self._system.accumulator -= value
                #! if negative 2's complement it
                return L_AM.Legal
            case "CLR":
                self._system.accumulator = 0
                return L_AM.Ignored
            case "COM":
                self._system.accumulator = ~self._system.accumulator
                return L_AM.Ignored
            case "AND":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095

                self._system.accumulator = self._system.accumulator & value

                return L_AM.Legal
            case "OR":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095

                self._system.accumulator = self._system.accumulator | value

                return L_AM.Legal
            case "XOR":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095

                self._system.accumulator = self._system.accumulator ^ value

                return L_AM.Legal
            case "ADDX":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095

                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                reg_val = self._system.get_register(reg)

                self._system.set_register(reg, reg_val + value)

                return L_AM.Legal
            case "SUBX":
                if control.am == AM.IMMEDIATE:
                    value = control.ea
                else:
                    value = int(self._system.fetch_memory(control.ea), 16) % 4095

                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                reg_val = self._system.get_register(reg)

                self._system.set_register(reg, reg_val - value)

                return L_AM.Legal
            case "CLRX":
                bin_instr = f"{int(control.instr, 16):0{24}b}"
                reg = Register(int(bin_instr[-2:0]) + 1)

                self._system.set_register(reg, 0)

                return L_AM.Ignored
            case "J":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal
                self._pc = control.ea
                return L_AM.Legal
            case "JZ":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal
                if self._system.accumulator == 0:
                    self._pc = control.ea
                return L_AM.Legal
            case "JN":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal
                if self._system.accumulator < 0:
                    self._pc = control.ea
                return L_AM.Legal
            case "JP":
                if control.am == AM.IMMEDIATE:
                    return L_AM.Illegal
                if self._system.accumulator >= 0:
                    self._pc = control.ea
                return L_AM.Legal
