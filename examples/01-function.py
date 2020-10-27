#!/usr/local/bin/python3.9
"""
MIT License

Copyright (c) 2019 Nxt Games, LLC
Written by Jordan Maxwell 
08/06/2019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from panda3d_analyze import PStatContextStack, analyze


p3d.load_prc_file_data('', 'want-pstat-stack Debug')


@analyze
def sleeper(task):
    time.sleep(1)
    return task.again


def nostats(task):
    PStatContextStack.disconnect()
    exit()


if __name__ == '__main__':
    base = ShowBase()
    PStatContextStack.connect()
    base.taskMgr.add(sleeper)
    base.taskMgr.do_method_later(5, nostats, 'exit')
    base.run()
