# You can run me as follow:
#
#    WF=$HOME/_/wf
#    env PYTHONPATH=$WF/lib               \
#        RUST_BACKTRACE=1                 \
#        python $WF/src/weapon-factory.py

from WeaponFactory import core as WF

if __name__ == "__main__":
    WF.Engine(profiling=False).run()
