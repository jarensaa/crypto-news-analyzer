import unittest
import cryptoscraper

class TestCryptoscraper(unittest.TestCase):

    def test_configure_db(self):
        coll = cryptoscraper.configure_db()
        self.assertEqual(coll.name, "cryptocompare")


    def test_parse_time_frame(self):
        times = [("1.04.2018","1.10.2018", 27), ("12.08.2018", "29.10.2018", 12), ("29.08.2018","12.10.2018", 7)]

        for timeframe in times:
            ts_from, ts_to, correct_length = timeframe
            timestamps = cryptoscraper.parse_time_frame(ts_from, ts_to)
            self.assertEqual(len(timestamps), correct_length)

        with self.assertRaises(ValueError):
            cryptoscraper.parse_time_frame("12.04.2018", "12.03.2018")