import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import parameters
from . import fromfile

def get_samples():
    '''
    Get names of FASTQ files for which clustering has not yet been performed.

    Also, clean up any incomplete executions.
    '''
    # get all available sample names
    sample_names = [fn[:-6] for fn in os.listdir('fastq') if fn.endswith('.fastq')]
    # get samples that already have executions
    if os.path.isdir('execution'):
        executions = []
        for fn in os.listdir('execution'):
            execution_dir = f'execution/{fn}'
            if os.path.isdir(execution_dir):
                if fromfile.execution_valid(fn):
                    executions.append(fn)
                else:
                    subprocess.run(['rm', '-rf', execution_dir])
    else:
        executions = []    

    # filter out samples that already have executions
    to_analyze = [name for name in sample_names if name not in executions]

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
    print('Found', len(to_analyze), 'samples on which pbAA has not yet been run.')
    return to_analyze

def get_pbaa_cmd(sample_name):
    options = parameters.get['pbaa_options']
    guide = f'guides/{parameters.get["guide"]}'
    input_fastq = f'fastq/{sample_name}.fastq'
    output_prefix = f'execution/{sample_name}/{sample_name}'
    return f'pbaa cluster {" ".join(options)} {guide} {input_fastq} {output_prefix}'

def run_pbaa(sample_name) -> subprocess.CompletedProcess:
    cmd = get_pbaa_cmd(sample_name)
    return subprocess.run(cmd, 
                          shell=True, 
                          capture_output=True)

def on(samples):

    for sample_name in samples:
        pbaa_runs = []
        with ThreadPoolExecutor() as executor:
            for sample_name in samples:
                os.makedirs(f'execution/{sample_name}', exist_ok=True)
                future = executor.submit(run_pbaa, sample_name)
                pbaa_runs.append(future)

        failures = 0
        n_stderr = 0
        for pbaa_run in as_completed(pbaa_runs):
            run_result: subprocess.CompletedProcess = pbaa_run.result()
            pbaa_cmd = run_result.args
            # capture the first error, or at least stderr
            if run_result.returncode == 0:
                print(f'pbAA run "{pbaa_cmd}" completed successfully.')
                if run_result.stderr:
                    print('However, it wrote the following to stderr:')
                    print(run_result.stderr.decode("utf-8"))
            else:
                failures += 1
                if error == '': # only collect first error
                    error = f'pbAA run "{pbaa_cmd}" failed.\n' 
                    error += run_result.stderr.decode("utf-8")
                    error += '\n'
    if failures:
        print(f'pbAA runs failed for {failures} samples.')
    elif n_stderr:
        print(f'All pbAA runs completed successfully, however {n_stderr} wrote to stderr.')
    else:
        print('All pbAA runs completed successfully.')

def main():

    samples = get_samples()
    on(samples)    

if __name__ == '__main__':
    main()