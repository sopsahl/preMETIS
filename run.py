
from argparse import ArgumentParser

from src.tests import *
from src.preMETIS import preMETIS

class SITDTr(preMETIS):
    def transform(self):
        self.simplicial_reduction()
        self.indistinguishable_reduction()
        self.twin_reduction()
        self.degree_2_elimination()
        self.triangle_contraction()

class SITP12(preMETIS):
    def transform(self):
        self.simplicial_reduction(degree_threshold=12)
        self.indistinguishable_reduction()
        self.twin_reduction()
        self.path_compression()

class SIDTr12(preMETIS):
    def transform(self):
        self.simplicial_reduction(degree_threshold=12)
        self.indistinguishable_reduction()
        self.degree_2_elimination()
        self.triangle_contraction()
    
class SITD6(preMETIS):
    def transform(self):
        self.simplicial_reduction(degree_threshold=6)
        self.indistinguishable_reduction()
        self.twin_reduction()
        self.degree_2_elimination()
    
class SD18(preMETIS):
    def transform(self):
        self.simplicial_reduction(degree_threshold=18)
        self.degree_2_elimination()
    
class METIS(preMETIS):
    def transform(self):
        pass
BASE_TESTS = [
    METIS,
    SITDTr,
    SITP12,
    SIDTr12,
    SITD6, 
    SD18
]

BASE_WORKLOAD = [

]

if __name__ == "__main__":
    run(BASE_WORKLOAD, BASE_TESTS, 'base')