from .daemon import Daemon
from .wheeld import Wheeld

# daemonを追加するときDaemonを一番上にすること

class Ds(
    Daemon,
    Wheeld
    ):

    pass