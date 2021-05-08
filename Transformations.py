from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
import os
import json
from interfaces.SentenceTransformation import SentenceTransformation


def load(module, cls):
    my_class = getattr(module, cls.__name__)
    return my_class()


def load_test_cases(test_json):
    with open(test_json) as f:
        d = json.load(f)
        examples = d["test_cases"]
    return examples


class TransformationsList:

    def __init__(self, load_tests=False):
        transformations = []
        test_cases = []
        # iterate through the modules in the current package
        package_dir = Path(__file__).resolve()  # --> Transformations.py
        transformations_dir = package_dir.parent.joinpath("transformations")
        for (_, m, _) in iter_modules([transformations_dir]):
            t_py = import_module(f"transformations.{m}.transformation")
            t_js = os.path.join(transformations_dir, m, "test.json")
            tx = [load(t_py, cls) for cls in SentenceTransformation.__subclasses__() if hasattr(t_py, cls.__name__)]
            if len(tx) > 0:
                transformations.extend(tx)
                if load_tests:
                    test_cases.append(load_test_cases(t_js))
        self.transformations = transformations
        self.test_cases = test_cases

    def generate(self, sentence: str):
        print(f"Original Input : {sentence}")
        generations = {"Original": sentence}
        for transformation in self.transformations:
            generations[transformation.name()] = transformation.generate(sentence)
        return generations


def execute_test_cases():
    tx = TransformationsList(load_tests=True)
    for transformation, tests in zip(tx.transformations, tx.test_cases):
        for test in tests:
            input = test["input"]
            output = test["output"]
            print(f"Executing transformation: {transformation.name()} on {input}")
            assert output == transformation.generate(input), f"Should have generated {output}"
