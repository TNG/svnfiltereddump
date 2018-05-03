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
        mapper.map_input_rev_to_output_rev(14, 12)

        self.assertEqual(mapper.get_output_rev_for_input_rev(14), 12)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 12)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 13)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 15)

    def test_start_rev(self):
        # Map all revisions before start rev to start rev
        config = ConfigMock()
        config.start_rev = 17
        mapper = RevisionMapper(config)
        output_rev17 = mapper.map_input_rev_to_output_rev(17, 17)
        output_rev20 = mapper.map_input_rev_to_output_rev(18, 17)
        output_rev20 = mapper.map_input_rev_to_output_rev(19, 19)

        self.assertEqual(mapper.get_output_rev_for_input_rev(17), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(18), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(19), 19)
        self.assertEqual(mapper.get_output_rev_for_input_rev(0), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(1), 17)
        self.assertEqual(mapper.get_output_rev_for_input_rev(16), 17)
        self.assertRaises(Exception, mapper.get_output_rev_for_input_rev, 20)
