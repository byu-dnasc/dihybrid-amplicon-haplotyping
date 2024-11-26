import os

from . import parameters

# validate configuration data
for configuration in parameters.GENE_INFO.values():
    guide_filename = configuration['guide']
    if not os.path.exists(f'guides/{guide_filename}'):
        raise FileNotFoundError(f'Guide file {guide_filename} not found under guides.')