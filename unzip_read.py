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


def save_logistics_line(file_str):
    lines = file_str.split('\n')
    to_save = []
    for line in lines:
        if line.startswith('LOGISTICS_1'):
            # save everything but LOGISTICS_1\t
            to_save.append(line[12:])
    return to_save


def add_time(filename, line):
    if line:
        return line[:-1] + filename + ';'
    else:
        return ''


def add_time_path(filename, zip_path, line):
    line = add_time(filename, line)
    if line:
        return line[:-1] + zip_path + '\n'
    else:
        return ''


def get_zip_values(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as archive:
        for file in archive.filelist:
            file_str = archive.read(file).decode("utf-8")
            logistics_lines = save_logistics_line(file_str)
            for i, line in enumerate(logistics_lines):
                logistics_lines[i] = add_time_path(file.filename,
                                                   zip_file_path, line)
        return logistics_lines


def get_all_values_from_zips(root, pattern):
    zips = find_all_zips(root, pattern)
    lines = []
    for zip_file in zips:
        lines.extend(get_zip_values(zip_file))
    return lines


def lines_to_csv(lines):
    to_csv = ''.join(lines)
    with open('logistics_1.csv', 'w') as file:
        file.write(to_csv)


if __name__ == "__main__":
    root = './all_the_zips'
    pattern = "*.zip"
    lines = get_all_values_from_zips(root, pattern)
