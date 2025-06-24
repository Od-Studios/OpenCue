name = "pyoutline"

version = "1.4.11"

authors = ["Open Cue"]

description = """
    PyOutline library for OpenCue job construction.
    """

build_requires = ["python-3.11", "loguru"]

requires = [
    "python-3.11",
    "pycue-1.4.11",
]

tools = ["pycuerun"]

uuid = "repository.pyoutline"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
