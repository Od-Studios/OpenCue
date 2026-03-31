name = "cuebot"

version = "1.4.15"

authors = ["Open Cue Bot"]

description = """
    A render management system.
    """

build_requires = ["cmake-3"]

requires = []

tools = ["cuebot"]

variants = [
    ["platform-linux", "arch-x86_64"],
]

uuid = "repository.cuebot"


def commands():
    env.PATH.append("{root}/bin")
