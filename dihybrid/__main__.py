import os
import sys
import shutil
import subprocess

from . import parameters
from . import ht_analysis
from . import run_pbaa

if len(sys.argv) < 3:
    print("Usage: python -m dihybrid <gene> <command>")
    sys.exit(1)

# validate gene
gene = sys.argv[1].lower()
genes = [gene.lower() for gene in parameters.PARAMETERS.keys()]
if gene not in genes:
    print(f"Invalid gene '{gene}' specified. Valid options are: {', '.join(genes)}")
    sys.exit(1)

# set the gene parameter
parameters.GENE = gene

# run the specified command
command = sys.argv[2]

if command == "pbaa":
    assert shutil.which('pbaa'), "pbaa executable not found."
    assert shutil.which('sbatch'), "sbatch executable not found."
    samples = run_pbaa.get_samples()
    script = f'import dihybrid.run_pbaa; dihybrid.run_pbaa.on({samples})'
    script.replace('\'', '\\\'')
    python_cmd = f'python3 -c \\"{script}\\"'
    sbatch_cmd = ' '.join((
        'sbatch',
        '--nodes=1',
        '--time=01:00:00',
        '--mem-per-cpu=2G',
        f'--wrap="{python_cmd}"',
        f'--ntasks={len(samples)}',
    ))
    subprocess.run(sbatch_cmd, shell=True)
elif command == "ht":
    ht_analysis.main()
else:
    print(f"Unknown command: {command}")
    sys.exit(1)