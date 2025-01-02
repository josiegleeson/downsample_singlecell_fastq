# Downsample a single cell FASTQ file

Python script to downsample a cell barcode demultiplexed FASTQ file.

```
python downsample_fastq.py -i input.fastq.gz -o output.fastq.gz -n 50

python downsample_fastq.py -i input.fastq.gz -o output.fastq.gz -b barcodes.txt --reformat

python downsample_fastq.py -h
usage: downsample_fastq.py [-h] --input INPUT --output OUTPUT
                           [--num-cells NUM_CELLS] [--barcodes BARCODES]
                           [--reformat]

Downsample FASTQ file to keep reads from cell barcodes

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Input FASTQ file (can be gzipped)
  --output OUTPUT, -o OUTPUT
                        Output FASTQ file (gzipped)
  --num-cells NUM_CELLS, -n NUM_CELLS
                        Number of cells to randomly select (ignored if
                        --barcodes is provided)
  --barcodes BARCODES, -b BARCODES
                        File containing specified cell barcodes (one per line)
  --reformat, -r        Reformat read IDs to contain only the UUID

```

