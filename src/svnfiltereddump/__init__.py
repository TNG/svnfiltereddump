
from Main import run
#
# The Big Plan
#

# Decide what to do with a revision
from DumpController import DumpController, STRATEGY_DUMP_HEADER, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, STRATEGY_DUMP_SCAN, STRATEGY_BOOTSTRAP, DUMP_HEADER_PSEUDO_REV

# Generate the lumps for that
from DumpHeaderGenerator import DumpHeaderGenerator
from BootsTrapper import BootsTrapper
from DumpFilter import DumpFilter, UnsupportedDumpVersionException
from SyntheticDeleter import SyntheticDeleter
from RevisionIgnorer import RevisionIgnorer

# Build the lumps
from LumpBuilder import LumpBuilder
# Fix length fields, drop empty revisions
from LumpPostProcessor import LumpPostProcessor

#
# SVN Abstraction layer
#
from SvnLump import SvnLump
from SvnDumpReader import SvnDumpReader
from SvnDumpWriter import SvnDumpWriter
from SvnRepository import SvnRepository

#
# Helpers
#
from Config import Config
from InterestingPaths import InterestingPaths
from RevisionMapper import RevisionMapper
from CheckedCommandFileHandle import CheckedCommandFileHandle
from ContentTin import ContentTin
from ParentDirectoryLumpGenerator import ParentDirectoryLumpGenerator
