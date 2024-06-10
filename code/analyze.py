from omorfi import Omorfi

omorfi = Omorfi()
assert omorfi.segmenter is not None

import sys
word = sys.argv[1]
omorfi.segment(sys)
