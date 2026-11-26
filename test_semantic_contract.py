"""Offline contract/wiring tests, not a measurement of model output quality."""
import json,re,unittest
from pathlib import Path
import server
ROOT=Path(__file__).resolve().parent

class SemanticContract(unittest.TestCase):
    def test_prompt_sync(self):
        html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
        self.assertEqual(html,(ROOT/'index.html').read_text(encoding='utf-8'))
        embedded=json.loads(re.search(r'let initialPrompt=("(?:\\.|[^"\\])*")',html).group(1))
        self.assertEqual(embedded,server.DEFAULT_PROMPT)
        self.assertLess(embedded.index('最高优先级契约'),embedded.index('【等级】'))
        for phrase in ['首个完整语义单元','全文语义融合机制','独立复述原文','原作者','反向语义检查','人话-GPT语转换器做好了','反例（禁止）']:
            self.assertIn(phrase,embedded)
    def test_cases_reach_both_passes(self):
        cases=json.loads((ROOT/'semantic_cases.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(cases),10)
        for case in cases:
            self.assertTrue(case['must_preserve'] and case['must_avoid'] and case['must_fuse'] and case['bad_example'] and case['reference_example'])
            for style in server.STYLES:
                for level in range(1,6):
                    with self.subTest(source=case['input'],style=style,level=level):
                        calls=[]
                        def fake(cfg,system,user):
                            data=json.loads(user.split('\n',1)[1]);calls.append((system,data,user));return {'text':'模拟初稿' if len(calls)==1 else '模拟修订','warning':'','usage':{}}
                        d={'raw':case['input'],'prompt':server.DEFAULT_PROMPT,'config':{},'level':level,'style':style,'recursive':True,'audit':True}
                        result=server.convert(d,fake)
                        self.assertEqual(len(calls),2)
                        self.assertIn('融合表达核心命题',calls[0][2])
                        self.assertIn('禁止先独立复述人话',calls[0][2])
                        self.assertIn('双向语义保真审校',calls[1][0])
                        self.assertIn('逐项提取原文命题',calls[1][0])
                        self.assertIn('新增断言',calls[1][0])
                        self.assertIn('整体重写',calls[1][0])
                        self.assertIn('脱离原意的防御段落',calls[1][0])
                        for _,data,_ in calls:
                            self.assertEqual(data['source_text'],case['input']);self.assertEqual(data['level'],level);self.assertEqual(data['style'],style)
                        self.assertEqual(calls[1][1]['draft'],'模拟初稿')
                        self.assertEqual(result['text'],'模拟修订')
                        self.assertTrue(result['reviewed'])
if __name__=='__main__':unittest.main()
