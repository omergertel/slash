from confetti import Config
from .utils.conf_utils import Doc, Cmdline

__all__ = ["config"]

config = Config({
    "debug" : {
        "enabled" : False // Doc("Enter pdb on failures and errors") // Cmdline(on="--pdb"),
    },
    "sentry" : {
        "dsn" : None // Doc("Possible DSN for a sentry service to log swallowed exceptions. "
                            "See http://getsentry.com for details"),
    },
    "hooks" : {
        "swallow_exceptions" : False // Doc("If set, exceptions inside hooks will be re-raised"),
    }
})
