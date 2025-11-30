from enum import Enum


class Register(Enum):
    AC = 0
    X0 = 1
    X1 = 2
    X2 = 3
    X3 = 4


class System:
    def __init__(self, file_name: str, starting_addr: str | None):
        self.file = file_name
        self._memory: str = ["000000"] * 4096
        self._start_addr = 0
        self.accumulator = 0
        self.x0 = 0
        self.x1 = 0
        self.x2 = 0xFFF
        self.x3 = 0

        if starting_addr:
            self._start_addr = int(starting_addr, 16)
        pass

    def insert_memory(self, addr: int, data: str):
        print(hex(addr), data)
        self._memory[addr] = data

    def fetch_memory(self, addr: int) -> str:
        return self._memory[addr]

    def load_file(self):
        instr_cnt = 0
        source = open(f"input/{self.file}")
        offset = 0

        for line in source:
            instr_cnt += 1

            print(line.strip())
            print(line[7:9])
            # eof
            if line[7:9] == "01":
                break

            # start
            if line[7:9] == "02":
                offset = int(line[9:13], 16) << 4
            else:
                # The start code is ALWAYS character 3-6
                address = format(int(line[3:7], 16) + offset, "03X")
                # The byte count is ALWAYS character 1-2
                for i in range(0, int(line[1:3], 16), 3):
                    # The data ALWAYS start on character 9, and we read three bytes (six nibbles)
                    addr = int(address, 16) + i // 3
                    data = (
                        format(int(line[9 + (i + 2) * 2 : 11 + (i + 2) * 2], 16), "02X")
                        + format(
                            int(line[9 + (i + 1) * 2 : 11 + (i + 1) * 2], 16), "02X"
                        )
                        + format(int(line[9 + i * 2 : 11 + i * 2], 16), "02X")
                    )
                    self.insert_memory(addr, data)

            # checksum fail
            if self._test_line(line) != 0:
                raise ValueError(f"Format error input file: {self.file}")

        print(f"loaded {instr_cnt} instructions")
        print(f"starting addr:{hex(self._start_addr)}")

    def get_start_addr(self) -> int:
        return self._start_addr

    def get_register(self, register: Register) -> int:
        match register:
            case Register.AC:
                return self.accumulator
            case Register.X0:
                return self.x0
            case Register.X1:
                return self.x1
            case Register.X2:
                return self.x2
            case Register.X3:
                return self.x3

    def get_registers(self) -> str:
        return f"AC[{self.accumulator:0{6}X}] X0[{self.x0:0{3}X}] X1[{self.x1:0{3}X}] X2[{self.x2:0{3}X}] X3[{self.x3:0{3}X}]"

    def _test_line(self, line: str) -> int:
        sum = 0
        for i in range(0, len(line) // 2 - 1):
            sum += int(line[(i * 2) + 1 : (i * 2) + 3], 16)

        return sum % 256
