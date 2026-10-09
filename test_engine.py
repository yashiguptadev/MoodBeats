import unittest
from engine import recommend,MOODS
class TestEngine(unittest.TestCase):
    def test_all_moods(self):
        for mood in MOODS:
            result=recommend(mood,'Any',.6)
            self.assertEqual(len(result['recommendations']),8)
            self.assertEqual(len(result['playlist']),5)
            self.assertEqual(len({s['id'] for s in result['playlist']}),5)
            self.assertTrue(all(0<=s['score']<=1 for s in result['recommendations']))
    def test_ga_trace(self):
        result=recommend('happy','Bollywood',.8)
        trace=result['ga_trace']
        self.assertEqual(len(trace['history']),trace['generations'])
        self.assertEqual(trace['final_best']['fitness'],result['ga_fitness'])
        self.assertEqual(len(trace['final_best']['songs']),5)
        self.assertTrue(all(0<=entry['example']['child']['fitness']<=1 for entry in trace['history']))
    def test_genre(self):
        self.assertTrue(recommend('happy','Bollywood',.8)['recommendations'])
if __name__=='__main__':unittest.main()
