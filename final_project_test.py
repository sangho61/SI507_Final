import unittest
import sqlite3
from final_project import *


class TestDatabase(unittest.TestCase):

    def test_search_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT game_name, videoid, title FROM Combined'
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn('overwatch', result_list[0])
        self.assertEqual('fortnite', result_list[56][0])
        self.assertEqual('Overwatch: Tracer, Genji & Junkrat NERFED! - HUGE Lucio BUFF!', result_list[1][2])
        self.assertEqual(len(result_list), 176)
        self.assertEqual(len(result_list[0]), 3)

        sql = '''
            SELECT COUNT(videoid)
            FROM Combined
            GROUP BY videoid
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()


        self.assertEqual(result_list[0][0], 1)
        self.assertEqual(result_list[30][0], 1)
        self.assertFalse(result_list[40][0] > 1)
        self.assertFalse(result_list[100][0] > 1)

        conn.close()


    def test_contents_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT *
            FROM contents
            '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertFalse(result_list[0] is None)
        self.assertEqual(len(result_list[0]), 7)

        conn.close()

class TestPlot(unittest.TestCase):

    def setUp(self):
        self.g1_obj = Game('fortnite')
        self.g2_obj = Game('PUBG')

    def test_plot_view(self):
        try:
            plot_viewcount([self.g1_obj, self.g2_obj])
        except:
            self.fail()

    def test_ratio(self):
        try:
            plot_like_ratio(self.g1_obj)
        except:
            self.fail()

    def test_likes_comments(self):
        try:
            plot_likes_comments([self.g1_obj, self.g2_obj])
        except:
            self.fail()

    def test_comments(self):
        try:
            plot_commentcount([self.g1_obj, self.g2_obj])
        except:
            self.fail()



unittest.main()
