import argparse
import os
import re
from pathlib import Path
from logging import Logger, INFO

logger = Logger(level=INFO)

# -> {req1: [line1, line2], req2: ...}
def get_requirements(path: str) -> dict:
    result = {}
    
    with open(path, 'r') as file:
        add_prev_line = False
        line_index = 0
        for line in file.readlines():
            line_index += 1
            req_name = re.match('^[\w-]+', line)
            if not req_name: # skip empty lines
                continue
            req_name = req_name.group(0).lower()
            
            pip_command = line.startswith('--')
            
            if pip_command:
                add_prev_line = True
            else:
                result[req_name] = [line_index]
                if add_prev_line:
                    result[req_name].append(line_index-1)
        
    return result             


def get_imported_deps(project_path: str) -> list:
    result = set()
    python_files = Path(project_path).rglob('*.py')
    
    for file_path in python_files:
        if '/site-packages/' in str(file_path):
            # skip python file from installed packages
            continue
        
        with open(file_path, 'r') as file_reader:
            for line in file_reader.readlines():
                import_line = re.match('^(import|from)\s+([\w]+)', line)
                if import_line:
                    result.add(import_line.group(2).lower())
                else:
                    # no more import lines -> skip
                    break
    
    return result

def delete_lines_from_file(path: str, lines_to_delete: list):
    lines = None
    with open(path, 'r') as f:
        lines = f.readlines()
    with open(path, 'w') as f:
        for idx, line in enumerate(lines):
            if idx not in lines_to_delete:
                f.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Requirements auto-cleaner')
    parser.add_argument('project', type=str, help="Project's root path")
    parser.add_argument(
        '-r', type=str, help="Requirements file alternative path relative to project's root", default='requirements.txt')
    # parser.add_argument('--dry-run', dest='dryrun', action='store_true', help="Don't write the results to a file")
    # parser.set_defaults(dryrun=False)

    args = parser.parse_args()
    req_file_path = os.path.join(args.project, args.r)

    reqs = get_requirements(req_file_path)
    logger.debug('Requirements mapping:\n', reqs)
    deps = sorted(get_imported_deps(args.project), key=len)
    logger.debug('Imports mapping:\n', deps)
    logger.debug('-----------')

    # check lines to delete
    delete_lines = []
    tentative_lines = []
    for req, lines in reqs.items():
        if req not in deps:
            if '-' in req:
                tentative_lines.append((req, lines))
            else:
                delete_lines += lines
        else:
            deps.remove(req)

    logger.info('Deleteing the following lines:', delete_lines)
    delete_lines_from_file(req_file_path, delete_lines)
    logger.info('You are clean!!')
    print('Needs a manual recheck:', tentative_lines)
