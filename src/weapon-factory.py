#!/usr/bin/env python

from WeaponFactory import Engine as WF

if __name__ == "__main__":
    import sys
    sys.exit( WF.Engine(profiling=False).run() )
