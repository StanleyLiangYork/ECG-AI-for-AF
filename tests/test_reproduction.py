import sys, unittest
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generate_figures import read,wilson

class ReproductionTests(unittest.TestCase):
    def test_prisma(self):
        c={r['key']:int(r['count']) for r in read('prisma.csv')}
        self.assertEqual(sum(c[k] for k in ['pubmed','wos','ieee','cdsr','central']),535)
        self.assertEqual(c['records']-c['duplicates'],c['screened'])
        self.assertEqual(c['screened']-c['excluded_screening'],c['assessed'])
        self.assertEqual(c['assessed']-c['excluded_full_text'],13)
        self.assertEqual(sum(c[k] for k in ['publication_type','component','af_result','population','ecg_input']),161)
    def test_appraisals(self):
        self.assertEqual(len(read('quadas.csv')),11)
        self.assertEqual(len(read('probast.csv')),10)
        r=read('grade.csv');self.assertEqual(len(r),35)
        self.assertEqual(len({x['id'] for x in r}),35)
        self.assertEqual(Counter(x['cert'] for x in r),{'moderate':6,'low':14,'very low':15})
        for x in r:
            self.assertEqual(x['inconsistency_display'],'NA')
            self.assertEqual(x['publication_bias_display'],'U')
    def test_intervals(self):
        lo,hi=wilson(54,114)
        self.assertAlmostEqual(lo,.3843877862,places=8)
        self.assertAlmostEqual(hi,.5646963472,places=8)
        for r in read('performance.csv'):
            self.assertTrue(0<=float(r['value'])<=1)
            if r['lower']:self.assertTrue(float(r['lower'])<=float(r['value'])<=float(r['upper']))
            if r['interval_type']=='wilson_95ci':self.assertAlmostEqual(float(r['value']),float(r['numerator'])/float(r['denominator']))
    def test_reference_map(self):
        r=read('references.csv');self.assertEqual(len(r),45)
        self.assertIn('Sethi',r[35]['citation']);self.assertIn('Tudjarski',r[33]['citation'])

if __name__=='__main__':unittest.main()
