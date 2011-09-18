
from unittest import TestCase

from svnfiltereddump import RevisionMapper

class ConfigMock(object):

    def __init__(self):
        self.renumber_revs = False
        self.start_rev = None


class RevisionMapperTest(TestCase):

    def test_simple(self):
        config = ConfigMock()
        mapper = RevisionMapper(config)
        output_rev = mapper.map_new_output_rev_for_input_rev(14)

        self.assertEqual(output_rev, 14)
        self.assertEqual(mapper.get_output_rev_for_input_rev(14), 14)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 13)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 15)

    def test_renumber_revs(self):
        # If 0 is not present as a input rev start numbering with 1
        config = ConfigMock()
        config.renumber_revs = True
        mapper = RevisionMapper(config)
        output_rev3 = mapper.map_new_output_rev_for_input_rev(3)
        output_rev4 = mapper.map_new_output_rev_for_input_rev(4)

        self.assertEqual(output_rev3, 1)
        self.assertEqual(output_rev4, 2)
        self.assertEqual(mapper.get_output_rev_for_input_rev(3), 1)
        self.assertEqual(mapper.get_output_rev_for_input_rev(4), 2)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 2)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 5)
        
    def test_renumber_revs_with_zero(self):
        config = ConfigMock()
        config.renumber_revs = True
        mapper = RevisionMapper(config)
        output_rev0 = mapper.map_new_output_rev_for_input_rev(0)
        output_rev4 = mapper.map_new_output_rev_for_input_rev(4)
        self.assertEqual(output_rev0, 0)
        self.assertEqual(output_rev4, 1)
        self.assertEqual(mapper.get_output_rev_for_input_rev(0), 0)
        self.assertEqual(mapper.get_output_rev_for_input_rev(4), 1)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 2)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 5)

    def test_start_rev(self):
        # Map all revisions before start rev to start rev
        config = ConfigMock()
        config.start_rev = 17
        mapper = RevisionMapper(config)
        output_rev17 = mapper.map_new_output_rev_for_input_rev(17)
        output_rev20 = mapper.map_new_output_rev_for_input_rev(20)

        self.assertEqual(output_rev17, 17)
        self.assertEqual(output_rev20, 20)
        self.assertEqual(mapper.get_output_rev_for_input_rev(17), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(20), 20)
        self.assertEqual(mapper.get_output_rev_for_input_rev(16), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(1), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(0), 17)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 18)

    def test_start_rev_with_renumber(self):
        config = ConfigMock()
        config.renumber_revs = True
        config.start_rev = 17
        mapper = RevisionMapper(config)
        output_rev17 = mapper.map_new_output_rev_for_input_rev(17)
        output_rev20 = mapper.map_new_output_rev_for_input_rev(20)
       
        self.assertEqual(output_rev17, 1)
        self.assertEqual(output_rev20, 2)
        self.assertEqual(mapper.get_output_rev_for_input_rev(17), 1)
        self.assertEqual(mapper.get_output_rev_for_input_rev(20), 2)
        self.assertEqual(mapper.get_output_rev_for_input_rev(16), 1)
        self.assertEqual(mapper.get_output_rev_for_input_rev(1), 1)
        self.assertEqual(mapper.get_output_rev_for_input_rev(0), 1)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 18)
     
