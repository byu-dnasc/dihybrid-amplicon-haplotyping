import os
from Bio.Align import PairwiseAligner
from Bio.Seq import Seq

from . import fromfile
from . import parameters

ALIGNER = PairwiseAligner()
ALIGNER.mode = 'local' # in case the sequences are not the same length
ALIGNER.match_score = 1
ALIGNER.mismatch_score = 0.9

HAPLOTYPES = parameters.get['haplotypes']
GUIDE_FILENAME = parameters.get['guide']
with open(f'guides/{GUIDE_FILENAME}', 'r') as f:
    lines = f.readlines()
    REF_SEQ = ''.join([l.strip() for l in lines[1:]])

def _get_alignment(query):
    alignment = ALIGNER.align(REF_SEQ, query)[0]
    rev_comp_alignment = ALIGNER.align(REF_SEQ, Seq(query).reverse_complement())[0]
    if alignment.score < rev_comp_alignment.score:
        alignment = rev_comp_alignment
    return alignment

def _get_haplotype(seq):
    pos_1 = parameters.get['SNP_1'] - 1
    pos_2 = parameters.get['SNP_2'] - 1
    alignment = _get_alignment(seq)
    snp_1, snp_2 = alignment[1,pos_1], alignment[1,pos_2]
    return (snp_1+snp_2).lower()

def write_clusters(cluster_rows):
    with open('clusters_by_haplotype.json', 'w') as f:
        header = ('sample_name', 'cluster_name', 'haplotype')
        f.write(','.join(header) + '\n')
        for line in cluster_rows:
            f.write(','.join(line) + '\n')

def write_csv(rows):
    # write the haplotype counts to a file
    with open('haplotype_counts.tsv', 'w') as f:
        header = ('sample_name', 'total_reads', 'reads_passing_qc') + tuple('haplotype_' + ht + '_reads' for ht in HAPLOTYPES)
        f.write('\t'.join(header) + '\n')
        for row in rows:
            f.write('\t'.join(str(x) for x in row) + '\n')

def main():
    assert os.path.isdir('execution'), 'No pbaa execution directory found. Run pbaa first.'
    incomplete_executions = []
    rows = []
    cluster_rows = []
    for sample_name in os.listdir('execution'):
        if not fromfile.execution_valid(sample_name):
            incomplete_executions.append(sample_name)
            continue
        ht_counts = {ht: 0 for ht in HAPLOTYPES}
        for cluster_name, seq, read_count, freq, possibly_chimeric in fromfile.get_clusters(sample_name):
            if freq < 0.05:
                continue
            haplotype = _get_haplotype(seq)
            assert haplotype in HAPLOTYPES, f'haplotype {haplotype} not among possible haplotypes {HAPLOTYPES} (sample_name={sample_name}, cluster_name={cluster_name})'
            ht_counts[haplotype] += read_count
            cluster_rows.append((sample_name, cluster_name, haplotype))
        total_reads = fromfile.get_total_num_reads(sample_name)
        reads_passing_qc = fromfile.get_num_input_reads(sample_name)
        rows.append((sample_name, total_reads, reads_passing_qc) + tuple(ht_counts[ht] for ht in HAPLOTYPES))

    print(f'pbAA execution(s) for {len(incomplete_executions)}',
          f'samples are incomplete: {' '.join(incomplete_executions)}')
    
    write_clusters(cluster_rows)
    write_csv(rows)

if __name__ == '__main__':
    main()