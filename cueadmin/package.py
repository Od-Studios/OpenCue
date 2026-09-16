name = "cueadmin"

version = "1.4.12"

authors = ["Open Cue"]

description = """
    CueAdmin commandline client for OpenCue administration.
    """

build_requires = ["python-3.11+<4", "loguru-0.7+<1"]

requires = [
    "python-3.11+<4",
    "pycue-1.4.11+<2",
    "pyoutline-1.4.11+<2",
]

tools = ["cueadmin"]

uuid = "repository.cueadmin"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
