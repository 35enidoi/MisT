from misskey import exceptions as mk_exceptions
from requests import exceptions as req_exceptions


__all__ = ["MisskeyPyExceptions"]


class MisskeyPyExceptions(
    mk_exceptions.MisskeyAPIException,
    req_exceptions.Timeout
):
    pass
