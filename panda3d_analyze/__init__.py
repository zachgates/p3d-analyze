#!/usr/local/bin/python3.9

__all__ = ['PStatTree']


import contextlib
import functools

from panda3d import core as p3d


@contextlib.contextmanager
def _PStatManager(collector):
    collector.start()
    yield
    collector.stop()


class _PStatBranch(dict):

    __slots__ = ('tree',)

    def __init__(self, tree: 'PStatTree'):
        if isinstance(tree, object):
            self.tree = tree
        else:
            raise ValueError(f'expected string value for name: {name}')

    def __getitem__(self, name: str):
        stat = (self.tree.name + ':' + name)
        if name in self:
            raise KeyError(f'stat already exists: {stat}')
        else:
            collector = p3d.PStatCollector(stat)
            self[name] = collector
            return collector

    get = __getitem__
        

def _PStatBranchFactory(name, bases, dct):
    try:
        global PStatTree
        return PStatTree
    except NameError:
        try:
            cls = type(name, bases, dct)
            return cls(name, (), {})
        except ConnectionError as exc:
            raise exc from None


class PStatTree(metaclass = _PStatBranchFactory):

    __slots__ = ('name',)
    _trunk = {}

    def __new__(cls, name, bases, dct):
        if bases and dct:
            assert (bases == (PStatTree,))
            name = dct.pop('__qualname__')
        else:
            assert (not bases) and (not dct)
            name = None

        inst = super().__new__(cls)
        inst.name = name
        return inst

    @property
    def client(self):
        return p3d.PStatClient.get_global_pstats()

    def __init__(self, name, bases, dct):
        if self.name is None:
            host = p3d.ConfigVariableString('pstats-host', 'localhost').value
            port = p3d.ConfigVariableInt('pstats-port', 5185).value
            if not self.client.connect(host, port):
                if p3d.ConfigVariableBool('pstats-required', False).value:
                    raise ConnectionError(f'failed to connect: {host}:{port}')
        else:
            self._trunk.setdefault(self.name, _PStatBranch(self))

    def __call__(self, str_or_func):
        if (self is PStatTree):
            assert isinstance(str_or_func, str)
            class _(PStatTree):
                __qualname__ = str_or_func
            return _
        else:
            collector = PStatTree._trunk[self.name][str_or_func.__name__]
            @functools.wraps(str_or_func)
            def pstat_func(*args, **kwargs):
                with _PStatManager(collector):
                    return str_or_func(*args, **kwargs)
            return pstat_func
