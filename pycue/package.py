name = "pycue"

version = "1.4.12"

authors = ["Open Cue"]

description = """
    Python API for OpenCue.
    """

build_requires = ["python-3.11", "loguru"]

requires = [
    "python-3.11",
    "PyYAML-6+<7",
    "six-1+<2",
    "future-1+<2",
    "grpcio-1.83+<2"
]

private_build_requires = ["grpcio_tools-1+<2", "grpcio-1+<2"]

uuid = "repository.pycue"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PYTHONPATH.prepend("{root}")
    env.CUEBOT_HOSTS.set("odfarm01")
