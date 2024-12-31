
import argparse
from sta_parser import read_ckt
from sta_parser import generate_delay_UT
from sta_parser import generate_slew_LUT
from traversal import main2
import traversal
import sys

# Set the new recursion limit
sys.setrecursionlimit(19000)

def main():
    parser = argparse.ArgumentParser(description="Bench file parser")
    parser.add_argument("--read_ckt", type=str, required=True, help="Filename of the circuit file (e.g., c17.bench)")
    parser.add_argument("--read_nldm", type=str, required=True,
                        help="Filename of the NLDM file (e.g., sample_NLDM.lib)")

    args = parser.parse_args()
    print(args.read_ckt)
    bench_file_name = args.read_ckt
    read_ckt(bench_file_name)
    generate_delay_UT(args.read_nldm)
    generate_slew_LUT(args.read_nldm)
    main2()




if __name__ == "__main__":
    print("Hello")
    main()