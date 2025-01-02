#!/usr/bin/env python3

import random
import gzip
from collections import defaultdict
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Downsample FASTQ file to keep reads from cell barcodes')
    parser.add_argument('--input', '-i', required=True, help='Input FASTQ file (can be gzipped)')
    parser.add_argument('--output', '-o', required=True, help='Output FASTQ file (gzipped)')
    parser.add_argument('--num-cells', '-n', type=int, help='Number of cells to randomly select (ignored if --barcodes is provided)')
    parser.add_argument('--barcodes', '-b', help='File containing specified cell barcodes (one per line)')
    parser.add_argument('--reformat', '-r', action='store_true', help='Reformat read IDs to contain only the UUID')
    return parser.parse_args()

def get_cell_barcode(header):
    """Extract cell barcode from read header"""
    return header.split('_')[0][1:]  # remove @ and get first part before _

def reformat_read_id(header):
    """
    Reformat read ID to keep only UUID
    """
    # split by '#' and get the UUID part
    uuid = header.split('#')[1].split('_')[0]
    return f"@{uuid}"

def read_barcodes_file(filename):
    """Read cell barcodes from file, handling both with and without @ prefix"""
    barcodes = set()
    with open(filename) as f:
        for line in f:
            barcode = line.strip()
            if barcode.startswith('@'):
                barcode = barcode[1:]
            barcodes.add(barcode)
    return barcodes

def process_fastq(input_file, output_file, num_cells=None, barcodes_file=None, reformat=False):
    if barcodes_file:
        # use provided barcodes
        selected_cells = read_barcodes_file(barcodes_file)
        print(f"Loaded {len(selected_cells)} cell barcodes from file")
    else:
        # get cell barcodes for random selection
        print("Collecting cell barcodes...")
        cell_barcodes = set()
        
        open_func = gzip.open if input_file.endswith('.gz') else open
        read_mode = 'rt' if input_file.endswith('.gz') else 'r'
        
        with open_func(input_file, read_mode) as f:
            while True:
                header = f.readline().strip()
                if not header:
                    break
                f.readline()  # sequence
                f.readline()  # +
                f.readline()  # quality
                
                cell_barcode = get_cell_barcode(header)
                cell_barcodes.add(cell_barcode)
        
        # randomly select cells
        print(f"Found {len(cell_barcodes)} unique cell barcodes")
        num_cells = num_cells or 50  # default to 50 if not specified
        selected_cells = set(random.sample(list(cell_barcodes), min(num_cells, len(cell_barcodes))))
        print(f"Randomly selected {len(selected_cells)} cells")
    
    # write selected reads to output
    print("Writing selected reads...")
    read_count = 0
    kept_count = 0
    cells_found = set()
    
    open_func = gzip.open if input_file.endswith('.gz') else open
    read_mode = 'rt' if input_file.endswith('.gz') else 'r'
    
    with open_func(input_file, read_mode) as fin, \
         gzip.open(output_file, 'wt') as fout:
        while True:
            header = fin.readline().strip()
            if not header:
                break
            seq = fin.readline().strip()
            plus = fin.readline().strip()
            qual = fin.readline().strip()
            
            read_count += 1
            cell_barcode = get_cell_barcode(header)
            
            if cell_barcode in selected_cells:
                # write header based on reformat option
                output_header = reformat_read_id(header) if reformat else header
                fout.write(f"{output_header}\n{seq}\n{plus}\n{qual}\n")
                kept_count += 1
                cells_found.add(cell_barcode)
    
    print(f"Processed {read_count} total reads")
    print(f"Kept {kept_count} reads from {len(cells_found)} cells")
    
    if barcodes_file:
        missing_cells = selected_cells - cells_found
        if missing_cells:
            print(f"Warning: {len(missing_cells)} requested cell barcodes were not found in the FASTQ file:")
            for barcode in sorted(missing_cells):
                print(f"  {barcode}")
    
    # write selected cell barcodes to file
    with open(output_file + '.barcodes.txt', 'w') as f:
        for barcode in sorted(cells_found):
            f.write(f"@{barcode}\n")

def main():
    args = parse_args()
    if not args.num_cells and not args.barcodes:
        args.num_cells = 50  # default to 50 cells if neither option is provided
    process_fastq(args.input, args.output, args.num_cells, args.barcodes, args.reformat)

if __name__ == '__main__':
    main()