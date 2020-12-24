#!/usr/local/bin/python3.9


import time

from direct.showbase.ShowBase import ShowBase

from panda3d_analyze import PStatTree


@PStatTree('Debug')
def sleeper(task):
    time.sleep(1)
    return task.again


def nostats(task):
    if PStatTree.client.is_connected():
        PStatTree.client.disconnect()
    exit()


if __name__ == '__main__':
    base = ShowBase()
    base.taskMgr.add(sleeper)
    base.taskMgr.do_method_later(5, nostats, 'disconnect')
    base.run()
