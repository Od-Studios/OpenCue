name = "pyoutline"

version = "1.4.13"

authors = ["Open Cue"]

description = """
    PyOutline library for OpenCue job construction.
    """

build_requires = ["python-3.11+<4", "loguru"]

requires = [
    "python-3.11+<4",
    "pycue-1.4.11+<2",
]

tools = ["pycuerun"]

uuid = "repository.pyoutline"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
