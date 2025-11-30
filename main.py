from components.sequencer import Sequencer
from components.system import System
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CPU GPU Final microprocessor emulator"
    )

    parser.add_argument(
        "--input",
        type=str,
        default="t1.obj",
        help="name of the hex file inside the input folder",
    )

    parser.add_argument(
        "--start_addr",
        type=str,
        help="hexadecimal starting address if none is defined in the program file",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    system = System(args.input, args.start_addr)
    sequencer = Sequencer(system)

    system.load_file()
    sequencer.start()
