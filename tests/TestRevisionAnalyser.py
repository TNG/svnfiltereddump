
from unittest import TestCase
from re import search

from svnfiltereddump import Config, RevisionAnalyser, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, STRATEGY_DUMP_SCAN, STRATEGY_BOOTSTRAP

class SvnRepositoryMock(object):
    def __init__(self):
        self.answers = { }
    def get_changed_paths_by_change_type_for_revision(self, rev):
        return self.answers[rev]

class InterestingPathMock(object):
    def is_interesting(self, path):
        return search('interesting', path) is not None
    def get_interesting_sub_directories(self, path):
        if search('interesting', path) is not None:
            return [ path ]
        if search('iparent', path):
            return [
                path + '/a',
                path + '/b',
                path + '/c'
            ]
        else:
            return [ ]


class TestRevisionAnalyser(TestCase):
    def setUp(self):
        self.config = Config( [ '/dummy' ] )
        self.interesting_paths = InterestingPathMock()
        self.repo = SvnRepositoryMock()
        self.analyser = RevisionAnalyser(self.config, self.repo, self.interesting_paths)

    def test_simple_interesting(self):
        self.repo.answers = {
            5: { 'A': [ 'a/interesting' ] }
        }
        
        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_interesting_modify(self):
        self.repo.answers = {
            5: { 'U': [ 'a/interesting' ] }
        }
        
        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_interesting_prop_modify(self):
        self.repo.answers = {
            5: { '_U': [ 'a/interesting' ] }
        }
        
        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_syntetic_delete_with_intresting_path(self):
        self.repo.answers = {
            10: { 'D': [ 'a/interesting', 'b/interesting' ] }
        }

        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [ 'a/interesting', 'b/interesting' ])

    def test_syntetic_delete_with_intresting_parents(self):
        self.repo.answers = {
            10: { 'D': [ 'iparent1', 'iparent2' ] }
        }

        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [
            'iparent1/a', 'iparent1/b', 'iparent1/c',
            'iparent2/a', 'iparent2/b', 'iparent2/c',
         ])
        
    def test_boring(self):
        self.repo.answers = {
            5: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring' ],
                'D': [ 'very/boring/statistics' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        }
        
        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(5)

        self.assertEqual(strategy, STRATEGY_IGNORE)
        self.assertEqual(deleted_paths, None)
   
    def test_complex_synthetic_delete(self):
        self.repo.answers = {
            10: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring' ],
                'D': [ 'iparent1', 'very/boring/statistics', 'c/interesting' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        }

        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [
            'iparent1/a', 'iparent1/b', 'iparent1/c',
            'c/interesting'
         ])

    def test_complex_interesting(self):
        self.repo.answers = {
            10: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring', 'more_interesting/than_the_deletes' ],
                'D': [ 'iparent1', 'iparent2', 'very/boring/statistics', 'c/interesting' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        }

        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(10)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_bootstrap(self):
        self.repo.answers = {
            5: { 'A': [ 'a/interesting' ] }
        }
        self.config.start_rev = 5
        
        ( strategy, deleted_paths ) = self.analyser.get_strategy_and_aux_data_for_revision(5)

        self.assertEqual(strategy, STRATEGY_BOOTSTRAP)
        self.assertEqual(deleted_paths, None)
         
