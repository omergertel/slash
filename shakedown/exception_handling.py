from contextlib import contextmanager
from .utils.debug import debug_if_needed
from . import hooks as trigger_hook
from .conf import config
import functools
import logbook
import raven
import sys

_logger = logbook.Logger(__name__)

def trigger_hooks_before_debugger(_):
    trigger_hook.exception_caught_before_debugger()
def trigger_hooks_after_debugger(_):
    trigger_hook.exception_caught_after_debugger()

_EXCEPTION_HANDLERS = [
    trigger_hooks_before_debugger,
    debug_if_needed,
    trigger_hooks_after_debugger,
    ]

@contextmanager
def handling_exceptions():
    try:
        yield
    except:
        handle_exception(sys.exc_info())
        raise

def handle_exception(exc_info):
    if not is_exception_handled(exc_info[1]):
        for handler in _EXCEPTION_HANDLERS:
            handler(exc_info)
    mark_exception_handled(exc_info[1])

def mark_exception_handled(e):
    mark_exception(e, "handled", True)

def is_exception_handled(e):
    """
    Checks if the exception ``e`` already passed through the exception handling logic
    """
    return bool(get_exception_mark(e, "handled", False))

_NO_DEFAULT = object()

def is_exception_marked(e, name):
    return get_exception_mark(e, name, _NO_DEFAULT) is not _NO_DEFAULT

def mark_exception(e, name, value):
    """
    Associates a mark with a given value to the exception ``e``
    """
    _ensure_exception_marks(e)[name] = value

def get_exception_mark(e, name, default=None):
    """
    Given an exception and a label name, get the value associated with that mark label.
    If the label does not exist on the specified exception, ``default`` is returned.
    """
    return _ensure_exception_marks(e).get(name, default)

def _ensure_exception_marks(e):
    returned = getattr(e, "__shakedown_exc_marks__", None)
    if returned is None:
        returned = e.__shakedown_exc_marks__ = {}
    return returned

@contextmanager
def get_exception_swallowing_context(report_to_sentry=True):
    """
    Returns a context under which all exceptions are swallowed (ignored)
    """
    try:
        yield
    except:
        if not get_exception_mark(sys.exc_info()[1], "swallow", True):
            raise
        if report_to_sentry:
            get_sentry_client().captureException()
        _logger.debug("Ignoring exception", exc_info=sys.exc_info())

def noswallow(exception):
    """
    Marks an exception to prevent swallowing by :func:`shakedown.exception_handling.get_exception_swallowing_context`,
    and returns it
    """
    mark_exception(exception, "swallow", False)
    return exception

def disable_exception_swallowing(func_or_exception):
    """
    Marks an exception to prevent swallowing. Can also be used as a decorator around a function to mark all escaped
    exceptions
    """
    if isinstance(func_or_exception, BaseException):
        return noswallow(func_or_exception)
    @functools.wraps(func_or_exception)
    def func(*args, **kwargs):
        try:
            return func_or_exception(*args, **kwargs)
        except BaseException as e:
            disable_exception_swallowing(e)
            raise
    return func


def get_sentry_client():
    return raven.Client(config.root.sentry.dsn)
