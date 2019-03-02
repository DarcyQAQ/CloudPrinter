#!/usr/bin/python3
#coding:utf-8

import hashlib
import json
import logging
import os
import traceback

# debug
import tornado.autoreload
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode

import cups

TMP_ROOT = '/Users/darcy-/Documents/Python/test/venv/files/'
ALLOW_TYPE_LIST = ['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
# pdf,xlsx,doc,docx,pptx
PASSWD = 'cnic@2019'

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/upload", UploadHandler),
            (r'/api/get_printers', GetPrintersHandler),
            (r'/api/print', PrintHandler),
            (r'/api/add_printers', AddPrinterHandler)
        ]
        tornado.web.Application.__init__(self, handlers, debug=True)

class AddPrinterHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # conn = cups.Connection()

        # conn.addPrinter(name=p_name)
        # conn.setPrinterLocation(p_name, loc)
        # conn.setPrinterInfo(p_name, inf)
        # conn.setPrinterDevice(p_name, uri_add)

        # printer_name = self.request.
        print self.request.body

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        filename = self.request.files['file'][0]['filename']
        file_type = self.request.files['file'][0]['content_type']
        data = self.request.files['file'][0]['body']
        print(filename, file_type)
        if file_type not in ALLOW_TYPE_LIST:
            self.write({'status': 'error', 'message': '不支持的类型'})
            return
        hl = hashlib.md5()
        hl.update(data)
        new_filename = hl.hexdigest()
        temp_path = TMP_ROOT + new_filename
        if os.path.exists(temp_path):
            self.write({'status': 'success', 'message': '文件已经存在', 'token': new_filename})
        else:
            with open(temp_path, 'wb') as fp:
                fp.write(data)
            self.write({'status': 'success', 'message': '上传成功', 'token': new_filename})

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class GetPrintersHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        conn = cups.Connection()
        printer_list = conn.getPrinters()

        tmp = []
        for name, printer in printer_list.items():
            tmp.append({
                'name': name,
                'position': printer['printer-location'] if len(printer['printer-location']) > 0 else '未知'
            })
        self.write({'status': 'success', 'data': tmp})

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class PrintHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        raw_data = self.request.body
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')
        data = json.loads(raw_data)
        file_path = TMP_ROOT + data['token']
        if len(data['token']) == 0 or not os.path.exists(file_path):
            self.write({
                'status': 'error',
                'message': '请先上传文件！'
            })
            return
        if data['password'] != PASSWD:
            self.write({
                'status': 'error',
                'message': '输入正确的密码'
            })
            return
        conn = cups.Connection()
        printer_list = conn.getPrinters()
        device = None
        for name in printer_list.keys():
            if name == data['printer']:
                device = name
                break
        if device is None:
            self.write({
                'status': 'error',
                'message': '非法的打印机！'
            })
            return
        if data['sides'] not in ['one-sided', 'two-sided-long-edge', 'two-sided-short-edge']:
            self.write({
                'status': 'error',
                'message': '非法的打印选项(sides)！'
            })
            return
        if data['color'] not in ['True', 'False']:
            self.write({
                'status': 'error',
                'message': '非法的打印选项(color)！'
            })
            return
        if not isinstance(data['copies'], int) or data['copies'] > 20:
            self.write({
                'status': 'error',
                'message': '非法的打印选项(copies <= 20)！'
            })
            return
        options = {
            'sides': data['sides'],
            'media': 'A4',
            'collate': 'true',
            'fit-to-page': 'true',
            'copies': str(data['copies']),
            'HPPJLColorAsGray': data['color']
        }
        tid = conn.printFile(device, file_path, data['token'], options)

        # content
        code = None
        msg = None
        reason = None
        printer_msg = []
        for printer, value in printer_list.items():
            printer_msg.append({
                'name': printer,
                'value': value
            })
            if printer == device:
                code = value['printer-state']
                msg = value['printer-state-message']
                reason = value['printer-state-reasons']
                print code
                print msg
                print reason
                print '------------------'
                break

        p_msg = str(msg) + str(reason)
        #
        if code == 0:
            self.write({'status': 'success', 'message': p_msg, 'data': {'task_id': tid}})
        else:
            self.write({'status': 'error', 'message': p_msg, 'data': {'task_id': tid}})

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                    # filename='/root/cnic-sign/cnic.log',
                    format='%(levelname)-8s %(filename)s:%(lineno)d\t'
                    '%(threadName)-10s: %(message)s')
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


