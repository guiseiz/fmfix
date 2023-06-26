import os
import re
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

folder_max_assets = {
    'EECA': 15999,
    'African': 11999,
    'Asian': 3999,
    'Caucasian': 15999,
    'Central European': 17999,
    'Italmed': 12999,
    'MENA': 5999,
    'MESA': 1991,
    'SAMed': 3999,
    'Scandinavian': 7999,
    'Seasian': 3999,
    'South American': 11999,
    'SpanMed': 7999,
    'YugoGreek': 9999
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        qs = parse_qs(body.decode('utf-8'))

        if 'file' not in qs:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'File parameter is missing.')
            return

        file_data = qs['file'][0]
        filename = 'config.xml'
        with open(filename, 'wb') as f:
            f.write(file_data.encode('utf-8'))

        corrected_filename = 'corrected_config.xml'
        correct_asset_names(filename, corrected_filename)

        with open(corrected_filename, 'rb') as f:
            corrected_file_data = f.read()

        os.remove(filename)
        os.remove(corrected_filename)

        self.send_response(200)
        self.send_header('Content-Disposition', 'attachment; filename=corrected_config.xml')
        self.send_header('Content-Type', 'application/xml')
        self.send_header('Content-Length', str(len(corrected_file_data)))
        self.end_headers()
        self.wfile.write(corrected_file_data)

def correct_asset_names(input_filename, output_filename):
    with open(input_filename, 'r') as file:
        lines = file.readlines()

    with open(output_filename, 'w') as file:
        for line in lines:
            match = re.search(r'from="([^"]+)/([^"]+)"', line)
            if match:
                folder = match.group(1)
                asset = match.group(2)

                if folder == 'UserAdded':
                    file.write(line)
                    continue

                if folder in folder_max_assets:
                    asset_match = re.match(r'([a-zA-Z\s]+)(\d+)', asset)
                    if asset_match:
                        asset_name = asset_match.group(1)
                        asset_number = int(asset_match.group(2))
                        if asset_name != folder or asset_number > folder_max_assets[folder]:
                            asset_name = folder
                            asset_number = random.randint(1, folder_max_assets[folder])
                            line = line.replace(match.group(0), f'from="{folder}/{asset_name}{asset_number}"')
            file.write(line)

if __name__ == '__main__':
    from http.server import HTTPServer
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting server...')
    httpd.serve_forever()
