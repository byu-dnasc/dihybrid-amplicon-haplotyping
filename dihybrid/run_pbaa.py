import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import parameters

def get_pbaa_cmd(sample_name):
    options = '--max-reads-per-guide=1000000 --max-uchime-score=0.01',
    guide=parameters.get['guide'],
    input_fastq=f'fastq/{sample_name}.fastq',
    output_prefix=f'execution/{sample_name}/{sample_name}'
    return f'pbaa cluster {options} {guide} {input_fastq} {output_prefix}'

def run_pbaa(sample_name) -> subprocess.CompletedProcess:
    cmd = get_pbaa_cmd(sample_name)
    return subprocess.run(cmd, 
                          shell=True, 
                          capture_output=True)

def get_samples():
    # find samples for which clustering has not yet been performed
    sample_names = [fn[:-6] for fn in os.listdir('fastq') if fn.endswith('.fastq')]
    if os.path.isdir('execution'):
        execution_names = [fn for fn in os.listdir('execution') if os.path.isdir('execution/'+fn)]
    else:
        execution_names = []    
    # exclude empty directories from executions
    for directory in execution_names:
        if os.listdir('execution/'+directory) == []:
            execution_names.remove(directory)

    to_analyze = [name for name in sample_names if name not in execution_names]

    # verify that an index file exists for each sample
    for sample_name in to_analyze:
        index_path = f'fastq/{sample_name}.fastq.fai'
        if not os.path.isfile(index_path):
            print(f'No index file found for {sample_name}, skipping.')
            to_analyze.remove(sample_name)

    # handle case where no samples need to be analyzed
    if not to_analyze:
        if sample_names:
            print('No samples found for which clusters have not been generated.')
        else:
            print('No samples found.')
        exit(1)

    # run pbaa on each sample
    print('Found', len(to_analyze), 'samples which pbAA has not yet been run on.')
    return to_analyze

def on(samples):

    for sample_name in samples:
        pbaa_runs = []
        with ThreadPoolExecutor() as executor:
            for sample_name in samples:
                os.makedirs(f'execution/{sample_name}', exist_ok=True)
                future = executor.submit(run_pbaa, sample_name)
                pbaa_runs.append(future)

        failures = 0
        error = ''
        for pbaa_run in as_completed(pbaa_runs):
            run_result: subprocess.CompletedProcess = pbaa_run.result()
            pbaa_cmd = run_result.args.join(' ')
            # capture the first error, or at least stderr
            if run_result.returncode != 0:
                failures += 1
                if error == '': # only collect first error
                    error = f'pbAA run "{pbaa_cmd}" failed.\n' 
                    error += run_result.stderr.decode("utf-8")
                    error += '\n'
            if run_result.stderr:
                if error == '': # only collect first error
                    error = f'pbAA run "{pbaa_cmd}" failed.\n'
                    error += run_result.stderr.decode("utf-8")
                    error += '\n'
    if failures:
        print(f'pbAA runs failed for {failures} samples. Only the first error is shown (below).')
        print(error)
    elif error: # i.e., no failures, but stderr was written
        print('All pbAA runs completed successfully, however at least one wrote to stderr. Only the first instance of this is shown (below).')
        print(error)
    else:
        print('All pbAA runs completed successfully.')

def main():

    samples = get_samples()
    on(samples)    

if __name__ == '__main__':
    main()