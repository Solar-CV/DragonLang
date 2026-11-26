import json, threading, unittest, urllib.request, urllib.error, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import server

class MockAPI(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_POST(self):
        payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.requests.append((self.path,payload,dict(self.headers)))
        if self.path.endswith('/chat/completions'):
            data={'choices':[{'message':{'content':'模拟龙语：'+('审校结果' if 'draft' in payload['messages'][1]['content'] else '首次结果')},'finish_reason':'stop'}],'usage':{'prompt_tokens':42,'completion_tokens':12}}
        elif self.path.endswith('/responses'): data={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'模拟 Responses'}]}]}
        elif self.path.endswith('/messages'): data={'content':[{'type':'text','text':'模拟 Claude'}],'stop_reason':'end_turn'}
        else: data={'candidates':[{'content':{'parts':[{'thought':True,'text':'ignore'},{'text':'模拟 Gemini'}]},'finishReason':'STOP'}]}
        b=json.dumps(data).encode();self.send_response(200);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)

def run_server(handler):
    s=ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=s.serve_forever,daemon=True).start();return s

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock=run_server(MockAPI);cls.mock.requests=[];cls.local=run_server(server.Handler);cls.base=f'http://127.0.0.1:{cls.mock.server_port}/v1';cls.url=f'http://127.0.0.1:{cls.local.server_port}'
    @classmethod
    def tearDownClass(cls):
        for s in (cls.mock,cls.local):s.shutdown();s.server_close()
    def config(self,p='chat'):return {'provider':p,'base':self.base,'model':'mock-model','key':'fake-key','limit':4096,'role':'developer','tokenField':'max_completion_tokens'}
    def data(self):return {'raw':'把按钮改蓝色。','prompt':server.DEFAULT_PROMPT,'style':'engineering','level':5,'recursive':True,'audit':False,'config':self.config()}
    def test_protocols(self):
        for p in ['chat','responses','anthropic','gemini']:
            with self.subTest(p=p):
                result=server.invoke(self.config(p),'SYSTEM','USER');self.assertIn('模拟',result['text']);path,body,headers=self.mock.requests[-1];self.assertNotIn('ignore',result['text']);self.assertIn('SYSTEM',json.dumps(body));self.assertIn('USER',json.dumps(body));self.assertIn('fake-key',str(headers))
    def test_two_pass(self):
        d=self.data();d['audit']=True;start=len(self.mock.requests);out=server.convert(d);self.assertTrue(out['reviewed']);self.assertEqual(len(self.mock.requests)-start,2);self.assertIn('审校结果',out['text']);self.assertIn('把按钮改蓝色',self.mock.requests[-1][1]['messages'][1]['content'])
    def test_fallback(self):
        d=self.data();d['audit']=True;calls=[]
        def fake(c,s,u):
            calls.append(u)
            if len(calls)>1:raise ValueError('simulated failure')
            return {'text':'初次结果','usage':{},'warning':''}
        r=server.convert(d,fake);self.assertEqual(r['text'],'初次结果');self.assertFalse(r['reviewed']);self.assertIn('未完成',r['warning'])
    def test_validation(self):
        d=self.data();d['raw']='';self.assertRaises(ValueError,server.convert,d);self.assertRaises(ValueError,server.endpoint,'http://example.com/v1','/chat/completions');self.assertRaises(ValueError,server.endpoint,'https://example.com/v1?secret=key','/chat/completions')
    def test_http(self):
        with urllib.request.urlopen(self.url+'/') as r: html=r.read().decode();self.assertIn(server.TOKEN,html);self.assertNotIn('__SESSION_TOKEN__',html)
        with urllib.request.urlopen(self.url+'/api/prompt') as r:self.assertEqual(json.load(r)['prompt'],server.DEFAULT_PROMPT)
        body=json.dumps(self.data()).encode();headers={'Content-Type':'application/json','Origin':self.url,'X-Dragon-Token':server.TOKEN};req=urllib.request.Request(self.url+'/api/convert',data=body,headers=headers)
        with urllib.request.urlopen(req) as r:self.assertIn('首次结果',json.load(r)['text'])
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(urllib.request.Request(self.url+'/api/convert',data=body,headers={'Content-Type':'application/json'}))
        self.assertEqual(cm.exception.code,403)
if __name__=='__main__':unittest.main()
