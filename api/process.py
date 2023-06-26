import os
import re
import random

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

def correct_asset_names(input_data):
    lines = input_data.splitlines()

    output_lines = []
    for line in lines:
        match = re.search(r'from="([^"]+)/([^"]+)"', line)
        if match:
            folder = match.group(1)
            asset = match.group(2)

            if folder == 'UserAdded':
                output_lines.append(line)
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
        output_lines.append(line)

    return '\n'.join(output_lines)

def handle_request(request):
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

    if 'file' not in request.files:
        return {
            'statusCode': 400,
            'body': 'File parameter is missing.'
        }

    file_data = request.files['file'].decode('utf-8')
    corrected_file_data = correct_asset_names(file_data)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Disposition': 'attachment; filename=corrected_config.xml',
            'Content-Type': 'application/xml'
        },
        'body': corrected_file_data
    }
