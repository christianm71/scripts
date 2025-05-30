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
                    "safe": False,
                    "to_delete": False,
                }
            )

        elif entry.is_dir():
            parse_directory(entry.path, all_files_dict, **kwargs)


# =========================================================================================
for dir_path in args.dirs:
    logger.info(f"parsing directory {dir_path}")
    parse_directory(
        dir_path,
        all_files,
        include_hidden_files=args.include_hidden_files,
        allow_file_ext=args.allow_file_ext,
        deny_file_ext=args.deny_file_ext,
    )

for file_size in all_files:
    paths_same_size_list = all_files[file_size]

    if len(paths_same_size_list) == 1:
        continue

    for i1 in range(len(paths_same_size_list)):
        path1_dict = paths_same_size_list[i1]

        if path1_dict["to_delete"]:
            continue

        for i2 in range(i1 + 1, len(paths_same_size_list), 1):
            path2_dict = paths_same_size_list[i2]

            if path2_dict["to_delete"]:
                continue

            if path1_dict["safe"] and path2_dict["safe"]:
                continue

            if path1_dict["st_ino"] == path2_dict["st_ino"] and \
                   path1_dict["st_dev"] == path2_dict["st_dev"]:
                continue

            if not filecmp.cmp(path1_dict["path"], path2_dict["path"], False):
                continue

            if not args.rm:
                print(f"sum \"{path1_dict['path']}\" \"{path2_dict['path']}\"")
            else:
                file_to_rm_dict = None

                if path1_dict["safe"]:
                    file_to_rm_dict = path2_dict
                elif path2_dict["safe"]:
                    file_to_rm_dict = path1_dict
                elif args.rm_regex:
                    if re.search(r"%s" % args.rm_regex, path1_dict["path"]):
                        file_to_rm_dict = path1_dict
                    elif re.search(r"%s" % args.rm_regex, path2_dict["path"]):
                        file_to_rm_dict = path2_dict

                if not file_to_rm_dict:
                    file_to_rm_dict = path2_dict
                file_to_safe_dict = path1_dict if file_to_rm_dict == path2_dict else path2_dict

                file_to_rm_dict["to_delete"] = True
                file_to_safe_dict["safe"] = True

                print(f"rm \"{file_to_rm_dict['path']}\"")
                print(f"   # safe \"{file_to_safe_dict['path']}\"")

                if path1_dict == file_to_rm_dict:
                    break
