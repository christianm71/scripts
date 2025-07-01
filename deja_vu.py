#!/usr/bin/python3

import argparse
import filecmp
import logging
import os
import re

# =========================================================================================
parser = argparse.ArgumentParser(description="Identify identical files")

parser.add_argument("--dirs", nargs="+", required=True, help="Directories where to search")
parser.add_argument("--allow_file_ext", nargs="+", help="Allowed file extentions")
parser.add_argument("--deny_file_ext", nargs="+", help="Denied file extentions")
parser.add_argument("--rm", action="store_true", default=False,
                    help="Generate the command to delete files")
parser.add_argument("--include_hidden_files", action="store_true", default=False,
                    help="Include hidden files (those starting with '.')")
parser.add_argument("--rm_regex", help="The regular expression to select the file to remove")
parser.add_argument("--debug", help="Debug mode", action="store_true", default=False)

args = parser.parse_args()

all_files = {}

# =========================================================================================
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

logger = logging.getLogger()


# =========================================================================================
def parse_directory(path, all_files_dict, **kwargs):
    include_hidden_files = kwargs.get("include_hidden_files", False)
    allow_file_ext = kwargs.get("allow_file_ext", [])
    deny_file_ext = kwargs.get("deny_file_ext", [])

    if not os.access(path, os.R_OK):
        logger.warning(f"cannot access directory {path}")
        return

    for entry in os.scandir(path):
        if entry.is_file():
            if not include_hidden_files and entry.name.startswith('.'):
                continue

            file_name_without_ext, file_extention_with_dot = os.path.splitext(entry.name)
            file_extention = file_extention_with_dot.lstrip('.')

            if allow_file_ext and file_extention not in allow_file_ext:
                continue

            if deny_file_ext and file_extention in deny_file_ext:
                continue

            st_size = str(entry.stat(follow_symlinks=False).st_size)
            st_ino = entry.stat(follow_symlinks=False).st_ino
            st_dev = entry.stat(follow_symlinks=False).st_dev

            if not all_files_dict.get(st_size):
                all_files_dict[st_size] = []

            all_files_dict[st_size].append(
                {
                    "path": entry.path,
                    "st_ino": st_ino,
                    "st_dev": st_dev,
                    "status": 0,
                }
            )

        elif entry.is_dir():
            parse_directory(entry.path, all_files_dict, **kwargs)


# =========================================================================================
SAFE = 1
TO_DELETE = 2

for dir_path in args.dirs:
    logger.info(f"parsing directory {dir_path}")
    parse_directory(
        dir_path,
        all_files,
        include_hidden_files=args.include_hidden_files,
        allow_file_ext=args.allow_file_ext,
        deny_file_ext=args.deny_file_ext,
    )

if not args.debug:
    logging.disable(logging.CRITICAL)

for file_size in all_files:
    items_list = all_files[file_size]

    n = len(items_list)

    if n == 1:
        continue

    for i in range(0, n - 1, 1):
        for j in range(i + 1, n, 1):
            status1 = items_list[i]["status"]
            status2 = items_list[j]["status"]

            path1 = items_list[i]["path"]
            path2 = items_list[j]["path"]

            if status1 == SAFE and status2 == SAFE:
                logger.info(f"'{path1}' '{path2}' are both SAFE")
                continue

            if items_list[i]["st_ino"] == items_list[j]["st_ino"] and \
               items_list[i]["st_dev"] == items_list[j]["st_dev"]:
                logger.info(f"'{path1}' '{path2}' are same files")
                continue

            if not filecmp.cmp(path1, path2, False):
                logger.info(f"'{path1}' '{path2}' are different")
                continue

            if not args.rm:
                print(f"sum '{path1}' '{path2}'")
            else:
                to_delete = None

                if status1 == 0 and status2 in [SAFE, TO_DELETE]:
                    if status2 == SAFE:
                        logger.info(f"'{path1}' will be deleted, '{path2}' is SAFE")
                    else:
                        logger.info(f"'{path1}' will be deleted, '{path2}' is TO_DELETE")
                    to_delete = i

                elif status2 == 0 and status1 in [SAFE, TO_DELETE]:
                    if status1 == SAFE:
                        logger.info(f"'{path2}' will be deleted, '{path1}' is SAFE")
                    else:
                        logger.info(f"'{path2}' will be deleted, '{path1}' is TO_DELETE")
                    to_delete = j

                elif args.rm_regex:
                    if re.search(r"%s" % args.rm_regex, path1):
                        logger.info(f"'{path1}' will be deleted (match the regex), '{path2}' will be SAFE")
                        to_delete = i
                    elif re.search(r"%s" % args.rm_regex, path2):
                        logger.info(f"'{path2}' will be deleted (match the regex), '{path1}' will be SAFE")
                        to_delete = j

                else:
                    to_delete = j

                if to_delete is None:
                    continue

                to_safe = i if to_delete == j else j

                path_to_delete = items_list[to_delete]["path"]
                path_to_safe = items_list[to_safe]["path"]

                print(f"rm '{path_to_delete}'")
                print(f"   # safe '{path_to_safe}'")

                items_list[to_delete]["status"] == TO_DELETE
                items_list[to_safe]["status"] == SAFE
