import os
import sys
import argparse

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

__version__ = 0.01


def main(sysargs=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        "The command line tool to run the project")
    parser.add_argument("-v", "--version", action="version",
                        version=f"fixinergy {__version__}")
    parser.add_argument("-n", "--notebook",
                        help="The name of the notebook to run")

    if len(sysargs) < 1:
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)

    notebook_fn = args.notebook
    with open(notebook_fn) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=None)
    ep.preprocess(nb, {"metadata": {"path": os.path.dirname(__file__)}})

    # with open("test_executed.ipynb", "w", encoding="utf-8") as f:
    #     nbformat.write(nb, f)


if __name__ == "__main__":
    main()
