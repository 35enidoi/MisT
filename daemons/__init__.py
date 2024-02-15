from .daemon import Daemon
from .wheeld import Wheeld
from .anupd import Anupd

# daemonを追加するときDaemonを一番上にすること

class Ds(
    Daemon,
    Wheeld,
    Anupd
    ):

    pass