from unittest import TestCase
from re import search

from svnfiltereddump import Config, DumpController, STRATEGY_DUMP_HEADER, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, \
    STRATEGY_DUMP_SCAN, STRATEGY_BOOTSTRAP


class SvnRepositoryMock(object):
    def __init__(self):
        self.answers = {}
        self.last_rev = 1

    def get_changed_paths_by_change_type_for_revision(self, rev):
        return self.answers[rev]

    def get_youngest_revision(self):
        return self.last_rev


class InterestingPathMock(object):
    def is_interesting(self, path):
        return search('interesting', path) is not None

    def get_interesting_sub_directories(self, path):
        if path[-1:] == '/':
            path = path[:-1]
        if search('interesting', path) is not None:
            return [path]
        if search('iparent', path):
            return [
                path + '/a',
                path + '/b',
                path + '/c'
            ]
        else:
            return []


class RevsionHandlerMock(object):
    def __init__(self, name, test_case):
        self.name = name
        self.test_case = test_case

    def process_revision(self, rev, aux_data):
        log_message = str(rev) + '/' + self.name
        self.test_case.process_log.append(log_message)
        if aux_data:
            self.test_case.aux_data_by_rev[rev] = aux_data


class TestDumpController(TestCase):
    def setUp(self):
        self.config = Config(['/dummy'])
        self.interesting_paths = InterestingPathMock()
        self.repo = SvnRepositoryMock()
        handler_map = {}
        for strategy in [STRATEGY_DUMP_HEADER, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, STRATEGY_DUMP_SCAN,
                         STRATEGY_BOOTSTRAP]:
            handler_map[strategy] = RevsionHandlerMock(strategy, self)
        self.controller = DumpController(self.config, self.repo, self.interesting_paths, handler_map)
        self.process_log = []
        self.aux_data_by_rev = {}

    def test_simple_interesting(self):
        self.repo.answers = {
            1: {'A': ['a/interesting']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_simple_interesting_dir(self):
        self.repo.answers = {
            1: {'A': ['a/interesting/']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_add_above_interesting_dir(self):
        self.repo.answers = {
            1: {'A': ['a/iparent/']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_interesting_modify(self):
        self.repo.answers = {
            1: {'U': ['a/interesting']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_interesting_prop_modify(self):
        self.repo.answers = {
            1: {'_U': ['a/interesting']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_syntetic_delete_with_intresting_path(self):
        self.repo.answers = {
            1: {'D': ['a/interesting', 'b/interesting']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_SYNTHETIC_DELETES])
        self.assertEqual(self.aux_data_by_rev, {1: ['a/interesting', 'b/interesting']})

    def test_syntetic_delete_with_intresting_parents(self):
        self.repo.answers = {
            1: {'D': ['iparent1', 'iparent2']}
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_SYNTHETIC_DELETES])
        self.assertEqual(self.aux_data_by_rev, {
            1: [
                'iparent1/a', 'iparent1/b', 'iparent1/c',
                'iparent2/a', 'iparent2/b', 'iparent2/c',
            ]
        })

    def test_boring(self):
        self.repo.answers = {
            1: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring'],
                'D': ['very/boring/statistics'],
                '_U': ['xxx/boring/bla'],
            }
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_IGNORE])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_complex_synthetic_delete(self):
        self.repo.answers = {
            1: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring'],
                'D': ['iparent1', 'very/boring/statistics', 'c/interesting'],
                '_U': ['xxx/boring/bla'],
            }
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_SYNTHETIC_DELETES])
        self.assertEqual(self.aux_data_by_rev, {
            1: [
                'iparent1/a', 'iparent1/b', 'iparent1/c',
                'c/interesting'
            ]
        })

    def test_complex_interesting(self):
        self.repo.answers = {
            1: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring', 'more_interesting/than_the_deletes'],
                'D': ['iparent1', 'iparent2', 'very/boring/statistics', 'c/interesting'],
                '_U': ['xxx/boring/bla'],
            }
        }

        self.controller.run()
        self.assertEqual(self.process_log, ['-1/' + STRATEGY_DUMP_HEADER, '1/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_bootstrap(self):
        self.repo.answers = {
            5: {'A': ['a/interesting']},
            6: {'A': ['a/more_interesting']}
        }
        self.config.start_rev = 5
        self.repo.last_rev = 6

        self.controller.run()
        self.assertEqual(self.process_log,
                         ['-1/' + STRATEGY_DUMP_HEADER, '5/' + STRATEGY_BOOTSTRAP, '6/' + STRATEGY_DUMP_SCAN])
        self.assertEqual(self.aux_data_by_rev, {})

    def test_complex_example(self):
        self.repo.answers = {
            1: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring'],
                'D': ['very/boring/statistics'],
                '_U': ['xxx/boring/bla'],
            },
            2: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring', 'more_interesting/than_the_deletes'],
                'D': ['iparent1', 'iparent2', 'very/boring/statistics', 'c/interesting'],
                '_U': ['xxx/boring/bla'],
            },
            3: {
                'A': ['a/boring', 'b/boring'],
                'U': ['a/more_boring'],
                'D': ['iparent1', 'very/boring/statistics', 'c/interesting'],
                '_U': ['xxx/boring/bla'],
            },
            4: {'A': ['a/really_boring']},
            5: {'A': ['interesting']}
        }
        self.repo.last_rev = 5
        self.controller.run()
        self.assertEqual(self.process_log, [
            '-1/' + STRATEGY_DUMP_HEADER,
            '1/' + STRATEGY_IGNORE,
            '2/' + STRATEGY_DUMP_SCAN,
            '3/' + STRATEGY_SYNTHETIC_DELETES,
            '4/' + STRATEGY_IGNORE,
            '5/' + STRATEGY_DUMP_SCAN
        ])
        self.assertEqual(self.aux_data_by_rev, {
            3: [
                'iparent1/a', 'iparent1/b', 'iparent1/c',
                'c/interesting'
            ]
        })
