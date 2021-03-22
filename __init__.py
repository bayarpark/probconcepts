# algorithms
from alg.data import \
    ColumnsDescription, create_cd, read_cd, write_cd, \
    Sample, \
    PredicateEncoder, \
    PredicateTable

from alg.model import BaseModel
from alg.generator import build_spcr

# fix-points
from alg.structure import Object, FixPoint
from alg.fixpoint import fp

# lang
from lang.opers import Var
from lang.predicate import Predicate
from lang.regularity import Regularity

# utils
from utils.cluster import altair
