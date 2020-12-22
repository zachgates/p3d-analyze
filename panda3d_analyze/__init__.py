#!/usr/local/bin/python3.9

__all__ = ['PStatContextStack', 'PStatContext', 'analyze']


import contextlib
import functools

from typing import Callable, Mapping, Optional

from panda3d import core as p3d


class _PStatContextStack(type):
    """
    Manage the PStatClient, and the PStatContext objects in use.
    """

    _trees = p3d.ConfigVariableList('want-pstat-tree')

    def want_tree(self, name: str):
        """Get the pstat context config variable."""
        for n in range(self._trees.getNumUniqueValues()):
            if self._trees.getUniqueValue(n) == name:
                return True
        else:
            return False

    ###

    @property
    def client(cls) -> p3d.PStatClient:
        """Refers to the global pstats client object."""
        return p3d.PStatClient.get_global_pstats()

    def connect(cls, hostname: str = '', port: int = -1) -> bool:
        """Connect to a pstats server @hostname:port."""
        if not cls.client.is_connected():
            return cls.client.connect(hostname, port)
        return False

    def disconnect(cls) -> bool:
        """Disconnect from a pstats server, if connected."""
        if connected := cls.client.is_connected():
            cls.client.disconnect()
        return connected

    ###

    _ctx: Mapping[str, p3d.PStatCollector] = {}

    def get(cls, name: str, tree: str) -> Optional[p3d.PStatCollector]:
        """Retrieves, or otherwise creates, a PStatCollector instance."""
        if cls.want_tree():
            tree = cls._ctx.setdefault(tree, dict())
            if name in tree:
                return tree[name]
            else:
                return tree.setdefault(name, p3d.PStatCollector(name))
        else:
            return None


class PStatContextStack(metaclass = _PStatContextStack):
    pass


class PStatContext(contextlib.AbstractContextManager):
    """
    Context manager wrapper for PStatCollector functions.
    """

    __slots__ = ('name', 'stat')

    def __init__(self, name: str, tree: str):
        """Initialize the context with a name and PStatCollector."""
        if PStatContextStack.want_tree(tree):
            self.name = f'{tree}:{name}'
            self.stat = PStatContextStack.get(self.name, tree)
        else:
            self.name = self.stat = None

    def __enter__(self):
        return self.stat

    def __exit__(self, *exc):
        if self.stat:
            return self.stat.stop()
        return False # don't propagate exceptions


def analyze(func: Callable):
    """Decorator for wrapping an arbitrary function in a PStatContext."""
    @functools.wraps(func)
    def pstat_context(*args, **kwargs):
        with PStatContext(func.__name__, 'Debug'):
            return func(*args, **kwargs)
    return pstat_context
