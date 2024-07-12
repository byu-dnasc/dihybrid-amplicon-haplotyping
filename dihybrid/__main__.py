import os
import sys
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
    if not os.access('pbaa', os.X_OK):
        print("pbaa executable not found.")
        sys.exit(1)
    if not os.access('sbatch', os.X_OK):
        print("sbatch executable not found.")
        sys.exit(1)
    samples = run_pbaa.get_samples()
    script = f'from . import run_pbaa; run_pbaa.on({samples})'
    python_cmd = f"python3 -c '{script}'"
    sbatch_cmd = ' '.join((
        'sbatch', 
        '--nodes=1',
        '--time=01:00:00',
        '--mem-per-cpu=1G',
        f'--wrap="{python_cmd}"'
        f'--ntasks={len(samples)}',
    ))
    subprocess.run(sbatch_cmd, shell=True)
elif command == "ht":
    ht_analysis.main()
else:
    print(f"Unknown command: {command}")
    sys.exit(1)