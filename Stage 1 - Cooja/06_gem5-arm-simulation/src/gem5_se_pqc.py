from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import CustomResource
from gem5.utils.requires import requires

requires(isa_required=ISA.ARM)

board = SimpleBoard(
    clk_freq="64MHz",
    processor=SimpleProcessor(cpu_type=CPUTypes.MINOR, isa=ISA.ARM, num_cores=1),
    memory=SingleChannelDDR3_1600(size="512MB"),
    cache_hierarchy=PrivateL1PrivateL2CacheHierarchy(
        l1d_size="32KiB", l1i_size="32KiB", l2_size="256KiB"
    ),
)

board.set_se_binary_workload(CustomResource("/home/user/pqc_bench_arm"))

Simulator(board=board).run()
