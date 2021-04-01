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


def make_ideal(settings='example_settings.yml'):
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
            print(___make_scripts_for_ideal(params['model'], params['data'], i, workspace), file=f)
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
conclusions_to_calc = split(list(sample.pt), {n_cores})[{bucket - 1}]
model = BaseModel(sample=sample, base_depth=base_depth, fully_depth=fully_depth, confidence_level=confidence_level, negative_threshold=negative_threshold, rules_write_path='{workspace}') 

build_spcr(conclusions_to_calc, model)
"""
    return script


def ___make_scripts_for_ideal(md_params, data, bucket, workspace):
    script = f"""from probconcepts.alg.data import Sample, read_cd
from probconcepts.alg.model import BaseModel
from probconcepts.alg.fixpoint import fp
from probconcepts.lang.parser import decstr
from probconcepts.alg.structure import Object
import pandas as pd
import json

df = pd.read_csv('{data['sample_path']}')
cd = read_cd('{data['cd_path']}')
sample = Sample(data=df, cd=cd)
base_depth = {md_params['base_depth']}
fully_depth = {md_params['fully_depth']}
confidence_level = {md_params['confidence_level']}
negative_threshold = {md_params['negative_threshold']}
model = BaseModel(sample=sample, base_depth=base_depth, fully_depth=fully_depth, confidence_level=confidence_level, negative_threshold=negative_threshold)

rules = decstr('{data['rules_path']}' , {{k:v for k, v in zip(cd.features.values(), cd.type_dict.values())}})
buckets = [range(0, 47),
 range(47, 94),
 range(94, 141),
 range(141, 188),
 range(188, 235),
 range(235, 282),
 range(282, 329),
 range(329, 376),
 range(376, 423),
 range(423, 470),
 range(470, 517),
 range(517, 564),
 range(564, 611),
 range(611, 658),
 range(658, 705),
 range(705, 752),
 range(752, 799),
 range(799, 846),
 range(846, 893),
 range(893, 940),
 range(940, 987),
 range(987, 1034),
 range(1034, 1081),
 range(1081, 1128),
 range(1128, 1175),
 range(1175, 1222),
 range(1222, 1269),
 range(1269, 1316),
 range(1316, 1363),
 range(1363, 1410),
 range(1410, 1457),
 range(1457, 1504),
 range(1504, 1551),
 range(1551, 1598),
 range(1598, 1645),
 range(1645, 1692),
 range(1692, 1739),
 range(1739, 1786),
 range(1786, 1833),
 range(1833, 1880),
 range(1880, 1927),
 range(1927, 1974),
 range(1974, 2021),
 range(2021, 2068),
 range(2068, 2115),
 range(2115, 2162),
 range(2162, 2209),
 range(2209, 2256),
 range(2256, 2303),
 range(2303, 2350),
 range(2350, 2397),
 range(2397, 2444),
 range(2444, 2491),
 range(2491, 2538),
 range(2538, 2585),
 range(2585, 2632),
 range(2632, 2679),
 range(2679, 2726),
 range(2726, 2773)]
lits = [Object(df.iloc[i, :], sample.pt) for i in buckets[{bucket-1}]]
writename = '{workspace}' + 'ideal_{bucket}.json'
fp(lits, rules, model, writename)
    """
    return script


if __name__ == "__main__":
    import sys

    if sys.argv[1] == '-ideal':
        make_ideal(sys.argv[2])
    elif sys.argv[1] == '-full':
        make(sys.argv[2])
    elif sys.argv[1] == '-json':
        make_from_json(sys.argv[2])
    else:
        print('Unexpected mode. Maybe you mean\n-ideal \t or \n-full\n \t or\n-json?')
