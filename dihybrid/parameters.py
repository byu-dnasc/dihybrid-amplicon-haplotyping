PARAMETERS = {
    'ADRB1': {
        'SNP_1': 145, # 1-based index
        'SNP_2': 1165, # 1-based index
        'haplotypes': ('ag', 'ac', 'gc', 'gg'),
        'guide': 'adrb1.fa'
    },
    'ADRB2': {
        'SNP_1': 46, # 1-based index
        'SNP_2': 79, # 1-based index
        'haplotypes': ('gg', 'ag', 'gc', 'ac'),
        'guide': 'adrb2.fa'
    }
}

GENE = 'ADRB2'

get = PARAMETERS[GENE]