import yaml
import os
import pandas as pd
from alg.model import BaseModel
from alg.data import Sample
from alg.generator import build_spcr, read_cd


def make(settings='example_settings.yml'):
    with open(settings, 'r') as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    save_path = params['path']

    os.mkdir(save_path + "run")

    n_cores = params['pbs_settings']['n_cores']
    mem = params['pbs_settings']['mem']
    walltime = params['pbs_settings']['walltime']
    python = params['pbs_settings']['python']
    name = params['pbs_settings']['job_name']

    __make_scripts(params['model'], )

    with open(save_path + "run_all.sh", 'w') as f:
        script_run_all = __make_run_script(n_cores, name)
        print(script_run_all, file=f)

    for i in range(1, n_cores + 1):
        script_n = f'{name}_{i}'
        with open(f"{save_path}run/{script_n}.sh", 'w') as f:
            print(__make_run_scripts_for_each(mem, walltime, name, python, script_n), file=f)


def __make_run_script(n_cores, script):
    run_all = f"""#!/bin/bash
for scn in `seq 1 {n_cores}`; do
qsub run/{script}_{{scn}}.sh
done
"""
    return run_all


def __make_run_scripts_for_each(mem, walltime, name, python, script_n):
    script = f"""# !/bin/bash

# PBS -l select=1:ncups=1:mem={mem}
# PBS -l walltime:{walltime}
# PBS -N {name}

cd $PBS_O_WORKDIR
{python} {script_n}.py
echo "Script started on: `uname -n`"
"""
    return script


def __make_scripts(md_params, data):
    df = pd.read_csv(data['sample_path'])
    cd = read_cd(data['cd_path'])
    sample = Sample(data=df, cd=cd)
    model = BaseModel(sample=sample, **md_params)

    script = f""" df = pd.read_csv('{data['sample_path']})
cd = read_cd({data['cd_path']})
sample = Sample(data=df, cd=cd)
base_depth = {md_params['base_depth']}
fully_depth = {md_params['fully_depth']}
confidence_level = {md_params['confidence_level']}
model = BaseModel(sample=sample, base_depth=base_depth, fully_depth=fully_depth, confidence_level=confidence_level) 
conclusions_to_calc = list(sample.pt)[{left}:{right}]
"""
