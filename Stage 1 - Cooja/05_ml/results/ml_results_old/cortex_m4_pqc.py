import m5
from m5.objects import *
from m5.util import addToPath
import argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument("--cmd", required=True)
args, _ = parser.parse_known_args()

addToPath('/home/aalma/gem5/configs/deprecated/example')
addToPath('/home/aalma/gem5/configs')
from common import SimpleOpts, ObjectList
import Options, Simulation, CacheConfig, MemConfig
from common.Caches import *

sys.argv = [sys.argv[0], '--cpu-type=ArmTimingSimpleCPU',
            '--mem-type=DDR3_1600_8x8', '--cmd', args.cmd]

args = Options.addCommonOptions(argparse.ArgumentParser())
args, _ = args.parse_known_args()
args.cmd = parser.parse_known_args()[0].cmd
args.cpu_type = 'ArmTimingSimpleCPU'
args.num_cpus = 1
args.mem_type = 'DDR3_1600_8x8'
args.mem_size = '512MB'
args.sys_clock = '64MHz'
