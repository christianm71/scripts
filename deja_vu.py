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

args = parser.parse_args()

all_files = {}

# =========================================================================================
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)

logger = logging.getLogger()


# =========================================================================================
def parse_directory(path, **kwargs):
    global all_files

    include_hidden_files = kwargs.get("include_hidden_files", False)
    allow_file_ext = kwargs.get("allow_file_ext", [])
    deny_file_ext = kwargs.get("deny_file_ext", [])

    if not os.access(path, os.R_OK):
        logger.warning(f"cannot access directory {path}")
        return

    for entry in os.scandir(path):
        if entry.is_file():
            if include_hidden_files and re.match(r"\.", entry.name):
                continue

            file_extention = entry.name.split(".")[-1]

            if allow_file_ext and file_extention not in allow_file_ext:
                continue

            if deny_file_ext and file_extention in deny_file_ext:
                continue

            st_size = str(entry.stat(follow_symlinks=False).st_size)
            st_ino = entry.stat(follow_symlinks=False).st_ino
            st_dev = entry.stat(follow_symlinks=False).st_dev

            if not all_files.get(st_size):
                all_files[st_size] = {}

            all_files[st_size][entry.path] = {
                "st_ino": st_ino,
                "st_dev": st_dev,
                "safe": False,
                "to_delete": False,
                "checked": False,
            }

        elif entry.is_dir():
            parse_directory(
                entry.path,
                include_hidden_files=include_hidden_files,
                allow_file_ext=allow_file_ext,
                deny_file_ext=deny_file_ext,
            )


# =========================================================================================
for dir_path in args.dirs:
    logger.info(f"parsing directory {dir_path}")
    parse_directory(
        dir_path,
        include_hidden_files=args.include_hidden_files,
        allow_file_ext=args.allow_file_ext,
        deny_file_ext=args.deny_file_ext,
    )

for file_size in all_files:
    paths_same_size = all_files[file_size]

    if len(paths_same_size) == 1:
        continue

    for path1 in paths_same_size:
        data_path1 = paths_same_size[path1]

        if data_path1["to_delete"]:
            continue

        data_path1["checked"] = True

        for path2 in paths_same_size:
            data_path2 = paths_same_size[path2]

            if data_path2["to_delete"] or data_path2["checked"]:
                continue

            if data_path1["safe"] and data_path2["safe"]:
                continue

            if data_path1["st_ino"] == data_path2["st_ino"] and \
                   data_path1["st_dev"] == data_path2["st_dev"]:
                continue

            if not filecmp.cmp(path1, path2, False):
                continue

            if not args.rm:
                print(f"sum '{path1}' '{path2}'")
            else:
                file_to_rm = None

                if data_path1["safe"]:
                    file_to_rm = path2
                elif data_path2["safe"]:
                    file_to_rm = path1
                elif args.rm_regex:
                    if re.search(r"%s" % args.rm_regex, path1):
                        file_to_rm = path1
                    elif re.search(r"%s" % args.rm_regex, path2):
                        file_to_rm = path2

                if not file_to_rm:
                    file_to_rm = path2
                file_to_safe = path1 if file_to_rm == path2 else path2

                print(f"rm '{file_to_rm}'")
                print(f"   # safe '{file_to_safe}'")
                paths_same_size[file_to_safe]["safe"] = True
                paths_same_size[file_to_rm]["to_delete"] = True
