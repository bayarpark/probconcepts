import os

import yaml


def make_from_json(settings='example_settings.yml'):
    with open(settings, 'r') as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if params['data']['concl_json'] is None:
        raise ValueError('path to json file with predicates is required')

    save_path = params['path']

    try:
        os.mkdir(save_path + "run")
    except FileExistsError:
        pass

    concl_json = params['data']['concl_json']
    n_cores = params['pbs_settings']['n_cores']
    mem = params['pbs_settings']['mem']
    walltime = params['pbs_settings']['walltime']
    python = params['pbs_settings']['python']
    name = params['pbs_settings']['job_name']
    workspace = params['pbs_settings']['workspace']

    for i in range(1, n_cores + 1):
        script_n = f'{name}_{i}'

        with open(f"{save_path}run/{script_n}.py", 'w') as f:
            print(__make_scripts_concl(params['model'], params['data'], i, n_cores, workspace, concl_json), file=f)
        with open(f"{save_path}run/{script_n}.sh", 'w') as f:
            print(__make_run_scripts_for_each(mem, walltime, name, python, script_n), file=f)


def make(settings='example_settings.yml'):
    with open(settings, 'r') as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    save_path = params['path']

    try:
        os.mkdir(save_path + "run")
    except FileExistsError:
        pass

    n_cores = params['pbs_settings']['n_cores']
    mem = params['pbs_settings']['mem']
    walltime = params['pbs_settings']['walltime']
    python = params['pbs_settings']['python']
    name = params['pbs_settings']['job_name']
    workspace = params['pbs_settings']['workspace']

    for i in range(1, n_cores + 1):
        script_n = f'{name}_{i}'

        with open(f"{save_path}run/{script_n}.py", 'w') as f:
            print(__make_scripts(params['model'], params['data'], i, n_cores, workspace), file=f)
        with open(f"{save_path}run/{script_n}.sh", 'w') as f:
            print(__make_run_scripts_for_each(mem, walltime, name, python, script_n), file=f)


def __make_run_scripts_for_each(mem, walltime, name, python, script_n):
    script = f"""#!/bin/bash

#PBS -l select=1:ncpus=1:mem={mem},place=free
#PBS -l walltime={walltime}
#PBS -N {script_n}

cd $PBS_O_WORKDIR
{python} {script_n}.py
echo "Script started on: `uname -n`"
"""
    return script


def __make_scripts_concl(md_params, data, bucket, n_cores, workspace, concl_json):
    script = f"""from probconcepts.alg.data import Sample, read_cd
from probconcepts.alg.model import BaseModel
import pandas as pd
from probconcepts.utils import split
from probconcepts.alg.generator import build_spcr
from probconcepts.lang.predicate import Predicate
import json
    
with open('{concl_json}', 'r') as f:
    conclusions = json.load(f)
conclusions = list(map(Predicate.from_dict, conclusions))
df = pd.read_csv('{data['sample_path']}')
cd = read_cd('{data['cd_path']}')
sample = Sample(data=df, cd=cd)
base_depth = {md_params['base_depth']}
fully_depth = {md_params['fully_depth']}
confidence_level = {md_params['confidence_level']}
negative_threshold = {md_params['negative_threshold']}
conclusions_to_calc = split(conclusions, {n_cores})[{bucket - 1}]
model = BaseModel(sample=sample, base_depth=base_depth, fully_depth=fully_depth, confidence_level=confidence_level, negative_threshold=negative_threshold, rules_write_path='{workspace}') 

build_spcr(conclusions_to_calc, model)
"""
    return script


def __make_scripts(md_params, data, bucket, n_cores, workspace):
    script = f"""from probconcepts.alg.data import Sample, read_cd
from probconcepts.alg.model import BaseModel
import pandas as pd
from probconcepts.utils import split
from probconcepts.alg.generator import build_spcr

df = pd.read_csv('{data['sample_path']}')
cd = read_cd('{data['cd_path']}')
sample = Sample(data=df, cd=cd)
base_depth = {md_params['base_depth']}
fully_depth = {md_params['fully_depth']}
confidence_level = {md_params['confidence_level']}
negative_threshold = {md_params['negative_threshold']}
conclusions_to_calc = split(list(filter(lambda x: x.is_positive(), sample.pt)), {n_cores})[{bucket - 1}]
model = BaseModel(sample=sample, base_depth=base_depth, fully_depth=fully_depth, confidence_level=confidence_level, negative_threshold=negative_threshold, rules_write_path='{workspace}') 

build_spcr(conclusions_to_calc, model)
"""
    return script


if __name__ == "__main__":
    import sys

    if sys.argv[1] == '-full':
        make(sys.argv[2])
    elif sys.argv[1] == '-json':
        make_from_json(sys.argv[2])
    else:
        print('Unexpected mode. Maybe you mean\n-full\n \t or\n-json?')
