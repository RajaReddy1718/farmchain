import unittest

from routes.reports import should_auto_suspend


class ReportSuspensionTests(unittest.TestCase):
    def test_threshold_is_reached_at_five_reports(self):
        self.assertTrue(should_auto_suspend(5))

    def test_threshold_is_not_reached_below_five(self):
        self.assertFalse(should_auto_suspend(4))


if __name__ == "__main__":
    unittest.main()
