from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import os
import datetime

import argparse

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

#translate_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
#translate_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")

#translate_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-3.3B")
#translate_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-3.3B")


class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        
        # Set response headers
        self.send_header("Content-type", "text/plain")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        content_length = int(self.headers['Content-Length'])

        request_body = self.rfile.read(content_length).decode('utf-8')
        query_params = parse_qs(urlparse(self.path).query)

        parSourceLang=query_params.get('source', ["fin_Latn"])[0]
        parTargetLang=query_params.get('target', ["eng_Latn"])[0] # Yes, I am from finland. These are default parameter values

        tStart = datetime.datetime.now()
        translator = pipeline('translation', model=translate_model, tokenizer=translate_tokenizer, src_lang=parSourceLang, tgt_lang=parTargetLang, max_length = maxlength)
        tPipeline = datetime.datetime.now()

        print("Translating "+str(request_body)+"\nFrom "+str(parSourceLang)+ " to "+str(parTargetLang)+ "Content-Length="+str(content_length)+" max_length="+str(maxlength) )
        result=translator(str(request_body))
        tTranslationReady = datetime.datetime.now()

        #print("time to create pipeline="+str(tPipeline-tStart))
        #print("time to translate="+str(tTranslationReady-tPipeline))

        self.wfile.write(result[0].get("translation_text").encode('utf-8') ) #Yes, no injection, buffer overflow hack prevention
    def do_GET(self):
        if self.path != '/':
            self.send_error(404, 'File Not Found: {}'.format(self.path))
        # serve only static.html
        try:
            with open('static.html', 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File static.html read error: {}'.format(self.path))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example language translator server')
    parser.add_argument('-p', '--port', type=int, default=8000, help='TCP port number')
    parser.add_argument('-m', '--model', type=str, default='facebook/nllb-200-3.3B', help='Model name https://huggingface.co/facebook/nllb-200-1.3B, facebook/nllb-200-distilled-600M,facebook/nllb-200-3.3B etc..')
    parser.add_argument('-n', '--maxlength', type=int, default=400, help="max length")
    args = parser.parse_args()

    global translate_model 
    translate_model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    global translate_tokenizer 
    translate_tokenizer = AutoTokenizer.from_pretrained(args.model)
    global maxlength
    maxlength = args.maxlength

    server_address = ('', args.port)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server running model'+ args.model  +'on http://127.0.0.1:'+str(args.port))
    httpd.serve_forever()
