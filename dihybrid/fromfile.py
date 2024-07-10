import re
import os
import subprocess

def get_clusters(sample_name):
    '''Gets all clusters from output files of pbaa'''
    clusters = []
    path = f'execution/{sample_name}/{sample_name}_passed_cluster_sequences.fasta'
    with open(path, 'r') as f:
        clusters += f.read().split('>')[1:]
    path = f'execution/{sample_name}/{sample_name}_failed_cluster_sequences.fasta'
    with open(path, 'r') as f:
        clusters += f.read().split('>')[1:]
    
    for cluster_record in clusters:
        label, seq = cluster_record.split('\n', 1)
        read_count = re.search(r'ReadCount-(\d+)', label).group(1)
        if read_count == '1': # ignore singletons
            continue
        cluster_name = re.search(r'cluster-(\d+)', label).group(1)
        frequency = re.search(r'cluster_freq:(\d+\.\d+)', label).group(1)
        possibly_chimeric = True if not 'uchime_score:-1' in label else False # ignore at high volume
        yield cluster_name, seq.strip(), int(read_count), float(frequency), possibly_chimeric

def get_num_input_reads(sample_name):
    with open(f'execution/{sample_name}/{sample_name}_read_info.txt', 'r') as f:
        # count num newlines in file
        return sum(1 for _ in f)

def get_total_num_reads(sample_name):
    with open(f'fastq/{sample_name}.fastq.fai', 'r') as f:
        # count num newlines in file
        return sum(1 for _ in f)

def _get_bam2fastq_cmd(bam_path, fastq_path):
    return 'bam2fastq -u -o {output_path} {bam_path}'.format(
        output_path=fastq_path,
        bam_path=bam_path
    )

def _get_faidx_cmd(fastq_path):
    cmd_fmt = 'samtools faidx {fastq_path}'
    return cmd_fmt.format(fastq_path=fastq_path)

def get_fastq(input_path, fastq_name):

    # use bam2fastq to convert the bam file to fastq
    output_prefix_path = os.path.join('fastq', fastq_name)
    cmd = _get_bam2fastq_cmd(input_path, output_prefix_path)
    result = subprocess.run(cmd, shell=True, capture_output=True)
    result.check_returncode()

    # use samtools to index the fastq file
    fastq_path = output_prefix_path + '.fastq'
    cmd = _get_faidx_cmd(fastq_path)
    result = subprocess.run(cmd, shell=True, capture_output=True)
    result.check_returncode()