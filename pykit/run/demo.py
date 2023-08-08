#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Demo Script."""

import pickle

class MyException(Exception):
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

        super(MyException, self).__init__('arg1: {}, arg2: {}'.format(arg1, arg2))

    def __reduce__(self):
        return (MyException, (self.arg1, self.arg2))


original = MyException('foo', 'bar')
print (repr(original))
print (original.arg1)
print (original.arg2)

reconstituted = pickle.loads(pickle.dumps(original))
print (repr(reconstituted))
print (reconstituted.arg1)
print (reconstituted.arg2)
