import sys
import shutil
import subprocess

from . import parameters
from . import run_pbaa

if len(sys.argv) < 3:
    print("Usage: python -m dihybrid <gene> <command>")
    sys.exit(1)

# validate gene
gene = sys.argv[1].lower()
genes = [gene.lower() for gene in parameters.GENE_INFO.keys()]
if gene not in genes:
    print(f"Invalid gene '{gene}' specified. Valid options are: {', '.join(genes)}")
    sys.exit(1)

# set the gene parameter
parameters.set_gene(gene)
from . import ht_analysis

# run the specified command
command = sys.argv[2]

if command == 'pbaa':
    assert shutil.which('pbaa'), "pbaa executable not found."
    assert shutil.which('sbatch'), "sbatch executable not found."
    samples = run_pbaa.get_samples()
    python_code = f'from dihybrid import run_pbaa, parameters;' + \
                  f'parameters.set_gene(\'{gene}\');' + \
                  f'run_pbaa.on({samples})'
    shell_cmd = f'python3 -c "{python_code}"'
    shell_cmd = shell_cmd.replace('"', '\\"')
    sbatch_cmd = [
        'sbatch',
        f'--wrap="{shell_cmd}"',
        f'--ntasks={len(samples)}',
    ]
    options = parameters.get['slurm_options']
    sbatch_cmd = ' '.join(sbatch_cmd + options)
    subprocess.run(sbatch_cmd, shell=True)
elif command == 'ht':
    ht_analysis.main()
else:
    print(f'Unknown command: {command}')
    sys.exit(1)