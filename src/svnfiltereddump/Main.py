#!/usr/bin/env python

from sys import argv, stdout
from os import putenv
from os.path import basename
from string import join
import logging

from DumpController import DumpController, STRATEGY_DUMP_HEADER, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, STRATEGY_DUMP_SCAN, STRATEGY_BOOTSTRAP, DUMP_HEADER_PSEUDO_REV

from DumpHeaderGenerator import DumpHeaderGenerator
from BootsTrapper import BootsTrapper
from DumpFilter import DumpFilter
from SyntheticDeleter import SyntheticDeleter
from RevisionIgnorer import RevisionIgnorer

from LumpBuilder import LumpBuilder
from LumpPostProcessor import LumpPostProcessor

from SvnDumpWriter import SvnDumpWriter
from SvnRepository import SvnRepository

from Config import Config
from InterestingPaths import InterestingPaths
from ParentDirectoryLumpGenerator import ParentDirectoryLumpGenerator
from RevisionMapper import RevisionMapper

console_handler = None

def _setup_interesting_paths(config):
    interesting_paths = InterestingPaths()
    for path in config.include_paths:
        logging.info("Including path '%s'" % (path) )
        interesting_paths.mark_path_as_interesting(path)
    for path in config.exclude_paths:
        logging.info("EXCLUDING path '%s'" % (path) )
        interesting_paths.mark_path_as_boring(path)
    return interesting_paths

def _setup_early_logging():
    global console_handler
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(levelname)s %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    

def _setup_final_logging(config):
    global console_handler
    if config.quiet:
        console_handler.setLevel(logging.WARNING)
    
    if config.log_file:
        log_name = basename(argv[0])
        log_file_formatter = logging.Formatter('%(asctime)s ' + log_name + ' %(levelname)s %(message)s')
        log_file_handler = logging.FileHandler(config.log_file)
        log_file_handler.setLevel(logging.DEBUG)
        log_file_handler.setFormatter(log_file_formatter)
        logger = logging.getLogger()
        logger.addHandler(log_file_handler)

def run():
    _setup_early_logging()
    config = Config(argv[1:])
    _setup_final_logging(config)
    logging.info("Command line: " + join(argv, ' '))
    interesting_paths = _setup_interesting_paths(config)

    # Make sure that we get english error messages
    putenv('LC_MESSAGES', 'C')

    source_repository = SvnRepository(config.source_repository)

    revision_mapper = RevisionMapper(config)
    dump_writer = SvnDumpWriter(stdout)
    with LumpPostProcessor(config, revision_mapper, dump_writer) as lump_post_processor:
        lump_builder = LumpBuilder(config, source_repository, interesting_paths, lump_post_processor)
        parent_directory_lump_generator = ParentDirectoryLumpGenerator(interesting_paths, lump_builder)
        lump_post_processor.parent_directory_lump_generator = parent_directory_lump_generator

        revision_handlers_hash = {
            STRATEGY_DUMP_HEADER:           DumpHeaderGenerator(lump_builder),
            STRATEGY_IGNORE:                RevisionIgnorer(lump_builder),
            STRATEGY_SYNTHETIC_DELETES:     SyntheticDeleter(source_repository, lump_builder),
            STRATEGY_DUMP_SCAN:             DumpFilter(config, source_repository, interesting_paths, lump_builder),
            STRATEGY_BOOTSTRAP:             BootsTrapper(config, source_repository, interesting_paths, lump_builder)
        }

        controller = DumpController(
            config = config,
            repository = source_repository,
            interesting_paths = interesting_paths,
            revision_handlers_by_strategy = revision_handlers_hash
        )

        controller.run()
