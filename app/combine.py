import sys
from csv import reader, writer
import argparse

parser = argparse.ArgumentParser(description="Process input files and write to an output file.")

parser.add_argument(
    "-o", "--output",
    default="combined.csv",
    help="Path to the output file."
)

parser.add_argument(
    "input_files",
    nargs="+",          # One or more input files
    help="List of input files to process."
)

args = parser.parse_args()

print("Output file:", args.output)
print("Input files:", args.input_files)

final_data = []
for i, filename in enumerate(args.input_files):
    with open(filename, 'r') as fin:
        rdr = reader(fin)
        content = list(rdr)
        if i == 0:
            final_data += content[:2]
        final_data += content[2:]

print(*final_data[:10], "...", *final_data[-10:], sep='\n')

with open(args.output, 'w', newline='') as fout:
    wtr = writer(fout, delimiter=',')
    wtr.writerows(final_data)

