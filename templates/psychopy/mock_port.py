# -*- coding: utf-8 -*-
"""A no-hardware stand-in for the trigger device.

It mirrors the small slice of the PsychoPy ``parallel.ParallelPort`` interface that
lexsync relies on (``setData``). By default it prints each code, and with
``record=True`` it keeps each code in ``log`` instead, for checking a script's codes
in a test of your own. The generated PsychoPy script does not import it: it defines
a smaller ``MockPort`` of its own, which only prints, so that it is self-contained.
"""


class MockPort:
    """Record or print trigger codes instead of writing to hardware."""

    def __init__(self, record=False):
        self.record = record
        self.log = []

    def setData(self, data):
        value = int(data)
        if self.record:
            self.log.append(value)
        else:
            print("[lexsync mock trigger] %d" % value)
