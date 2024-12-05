GENE_INFO = {
    'adrb1': {
        'SNP_1': 145, # 1-based index
        'SNP_2': 1165, # 1-based index
        'haplotypes': ('ag', 'ac', 'gc', 'gg'),
        'guide': 'adrb1.fa'
    },
    'adrb2': {
        'SNP_1': 46, # 1-based index
        'SNP_2': 79, # 1-based index
        'haplotypes': ('gg', 'ag', 'gc', 'ac'),
        'guide': 'adrb2.fa'
    }
}

PBAA_DEFAULTS = [
    # '--max-reads-per-guide=1000000',
    '--max-uchime-score=0.01'
]

SLURM_DEFAULTS = [
    '--qos=normal',
    '--nodes=1',
    '--time=01:00:00',
    '--mem-per-cpu=4G'
]

get = {}
get['pbaa_options'] = PBAA_DEFAULTS
get['slurm_options'] = SLURM_DEFAULTS

def set_gene(gene):
    '''Add gene info to parameters'''
    global get
    get.update(GENE_INFO[gene])
