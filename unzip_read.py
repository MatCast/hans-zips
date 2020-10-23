import os
from fnmatch import fnmatch
import zipfile
from io import BytesIO


def find_all_zips(root, pattern):
    zips = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name, pattern):
                zips.append(os.path.join(path, name))
    return zips


def get_values(line):
    '''Return a line containing only the values after "=" sign.'''
    line_list = [col.split('=')[1] for col in line.split(';')[:-1]]
    line = ';'.join(line_list) + ';'
    return line


def get_headers(line):
    '''Return a line containing only the values before "=" sign.'''
    line_list = [col.split('=')[0] for col in line.split(';')[:-1]]
    line_list.extend(['START_TIME', 'ZIP_PATH'])
    line = ';'.join(line_list) + ';\n'
    return line


def add_first_file_headers(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as archive:
        if archive.filelist:
            file_str = archive.read(archive.filelist[0]).decode("utf-8")
            logistics_lines = get_logistics_line(file_str)
            if logistics_lines:
                return get_headers(logistics_lines[0])


def get_logistics_line(file_str):
    '''Retrurn all the line after the "LOGISTICS_1" value.'''
    lines = file_str.split('\n')
    to_save = []
    for line in lines:
        if line.startswith('LOGISTICS_1'):
            # save everything but LOGISTICS_1\t
            to_save.append(line[12:])
    return to_save


def add_time(filename, line):
    '''Add Start Time to the line based on the filename.'''
    if line:
        return line + filename.split('.')[0] + ';'
    else:
        return ''


def add_time_path(filename, zip_path, line):
    '''Add Start Time and zip path to the line.'''
    line = add_time(filename, line)
    if line:
        return line + zip_path + '\n'
    else:
        return ''


def get_zip_values(zip_path):
    all_lines = []
    with zipfile.ZipFile(zip_path, 'r') as archive:
        for file in archive.filelist:
            file_str = archive.read(file).decode("utf-8")
            logistics_lines = (get_logistics_line(file_str))
            for i, line in enumerate(logistics_lines):
                line = get_values(line)
                logistics_lines[i] = add_time_path(file.filename, zip_path,
                                                   line)
            all_lines.extend(logistics_lines)
        return all_lines


def get_all_values_from_zips(root, pattern):
    zips = find_all_zips(root, pattern)
    lines = []
    headers = ''
    for zip_file in zips:
        if not headers:
            headers = add_first_file_headers(zip_file)
            lines.append(headers)
        lines.extend(get_zip_values(zip_file))
    return lines


def lines_to_csv(lines, path='logistics_1.csv'):
    to_csv = ''.join(lines)
    with open(path, 'w') as file:
        file.write(to_csv)


if __name__ == "__main__":
    root = './all_the_zips'
    pattern = "*.zip"
    lines = get_all_values_from_zips(root, pattern)
    lines_to_csv(lines)
