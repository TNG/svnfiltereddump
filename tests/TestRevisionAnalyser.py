
from unittest import TestCase
from re import search

from svnfiltereddump import RevisionAnalyser, STRATEGY_IGNORE, STRATEGY_SYNTHETIC_DELETES, STRATEGY_DUMP_SCAN

class SvnRepositoryMock(object):
    def __init__(self, answers):
        self.answers = answers
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
    def test_simple_interesting(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            5: { 'A': [ 'a/interesting' ] }
        } )
        
        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_interesting_modify(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            5: { 'U': [ 'a/interesting' ] }
        } )
        
        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_interesting_prop_modify(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            5: { '_U': [ 'a/interesting' ] }
        } )
        
        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(5)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)

    def test_syntetic_delete_with_intresting_path(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            10: {
                'D': [ 'a/interesting', 'b/interesting' ]
                
            }
        } )

        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [ 'a/interesting', 'b/interesting' ])

    def test_syntetic_delete_with_intresting_parents(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            10: {
                'D': [ 'iparent1', 'iparent2' ]
                
            }
        } )

        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [
            'iparent1/a', 'iparent1/b', 'iparent1/c',
            'iparent2/a', 'iparent2/b', 'iparent2/c',
         ])
        
    def test_boring(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            5: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring' ],
                'D': [ 'very/boring/statistics' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        } )
        
        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(5)

        self.assertEqual(strategy, STRATEGY_IGNORE)
        self.assertEqual(deleted_paths, None)
   
    def test_complex_synthetic_delete(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            10: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring' ],
                'D': [ 'iparent1', 'very/boring/statistics', 'c/interesting' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        } )

        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(10)

        self.assertEqual(strategy, STRATEGY_SYNTHETIC_DELETES)
        self.assertEqual(deleted_paths, [
            'iparent1/a', 'iparent1/b', 'iparent1/c',
            'c/interesting'
         ])

    def test_complex_interesting(self):
        i_paths = InterestingPathMock()
        repo = SvnRepositoryMock( {
            10: {
                'A': [ 'a/boring', 'b/boring' ],
                'U': [ 'a/more_boring', 'more_interesting/than_the_deletes' ],
                'D': [ 'iparent1', 'iparent2', 'very/boring/statistics', 'c/interesting' ],
                '_U': [ 'xxx/boring/bla' ],
            }
        } )

        a = RevisionAnalyser(repo, i_paths)
        ( strategy, deleted_paths ) = a.get_strategy_and_delete_paths_for_revision(10)

        self.assertEqual(strategy, STRATEGY_DUMP_SCAN)
        self.assertEqual(deleted_paths, None)
         
