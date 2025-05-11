
from argparse import ArgumentParser

from src.tests import run
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
    SITP12,
    SIDTr12,
    SITD6, 
    SD18
]

TEST_NAME_MAP = {cls.__name__: cls for cls in BASE_TESTS}

ROAD_NETWORKS = {
    'roadNet-TX': 'roadNet-TX.txt',
    'roadNet-CA': 'roadNet-CA.txt',
    'roadNet-PA': 'roadNet-PA.txt'
}

SOCIAL_NETWORKS = {
    'email-Enron': 'email-Enron.txt',
    'ca-GrQc': 'ca-GrQc.txt',
    'com-amazon': 'com-amazon.ungraph.txt',
}

ALL_WORKLOADS = {
    'road': ROAD_NETWORKS,
    'social': SOCIAL_NETWORKS,
}

def main():
    parser = ArgumentParser(description="Run preMETIS test suite on SNAP datasets.")
    parser.add_argument('--workload', choices=ALL_WORKLOADS.keys(), required=True,
                    help='Choose the type of network workload: road, social')
    parser.add_argument('--tests', nargs='+', choices=list(TEST_NAME_MAP.keys()) + ['all'], default=['all'],
                    help='Specify which tests to run, or "all" for all tests')
    args = parser.parse_args()

    workload = ALL_WORKLOADS[args.workload]

    if 'all' in args.tests:
        tests_to_run = list(TEST_NAME_MAP.values())
    else:
        tests_to_run = [TEST_NAME_MAP[name] for name in args.tests]

    run(workload, tests_to_run)


if __name__ == "__main__":
    main()