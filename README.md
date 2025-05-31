# Available Scripts

This repository contains a collection of useful scripts.

*   **`deja_vu.py`**: A Python script to find and manage duplicate files.
*   **`update-system.bash`**: A shell script to update system packages on Debian-based Linux distributions.

---
## Deja Vu - Duplicate File Finder

### Overview

Deja Vu is a Python script designed to help you find and optionally manage duplicate files across one or more directories. It identifies files that are identical in content, providing options to filter the search and generate commands for removal.

### Features

- Scans one or more specified directories recursively.
- Identifies duplicate files efficiently, first by comparing file sizes and then by performing a byte-by-byte comparison for files of the same size.
- Supports inclusion of hidden files (files starting with a `.`) in the scan.
- Allows filtering of files based on allowed file extensions (e.g., only scan `.jpg`, `.png`).
- Allows filtering of files based on denied file extensions (e.g., ignore `.log`, `.tmp` files).
- Can generate `rm` (remove) commands for duplicate files, making cleanup easier.
- Provides a mechanism to specify which duplicate file to remove using a regular expression that matches the file path.

### Usage (Command-Line Arguments)

The script is controlled via command-line arguments. Below is the help text detailing the available options:

```
usage: deja_vu.py [-h] --dirs DIRS [DIRS ...]
                  [--allow_file_ext ALLOW_FILE_EXT [ALLOW_FILE_EXT ...]]
                  [--deny_file_ext DENY_FILE_EXT [DENY_FILE_EXT ...]] [--rm]
                  [--include_hidden_files] [--rm_regex RM_REGEX]

Identify identical files

options:
  -h, --help            show this help message and exit
  --dirs DIRS [DIRS ...]
                        Directories where to search
  --allow_file_ext ALLOW_FILE_EXT [ALLOW_FILE_EXT ...]
                        Allowed file extentions
  --deny_file_ext DENY_FILE_EXT [DENY_FILE_EXT ...]
                        Denied file extentions
  --rm                  Generate the command to delete files
  --include_hidden_files
                        Include hidden files (those starting with '.')
  --rm_regex RM_REGEX   The regular expression to select the file to remove
```

### Examples

Here are a few examples of how to use `deja_vu.py`:

1.  **Basic duplicate search in two directories:**
    This command will search for duplicate files in `/path/to/photos` and `/path/to/backup_photos`.

    ```bash
    python deja_vu.py --dirs /path/to/photos /path/to/backup_photos
    ```

2.  **Search including hidden files and filtering by text files:**
    This command will search for duplicate `.txt` and `.md` files in `~/documents`, including any hidden files.

    ```bash
    python deja_vu.py --dirs ~/documents --include_hidden_files --allow_file_ext txt md
    ```

3.  **Search and generate remove commands, preferring to remove files from a 'tmp' directory:**
    This command will search for duplicates between `/projects` and `/projects/tmp_backup`. If duplicates are found, it will suggest `rm` commands, prioritizing the removal of files located in paths containing `/tmp_backup/`.

    ```bash
    python deja_vu.py --dirs /projects /projects/tmp_backup --rm --rm_regex "/tmp_backup/"
    ```

This will output lines like:
`rm '/projects/tmp_backup/duplicate_file.zip'`
`   # safe '/projects/original_file.zip'`

---

## `update-system.bash` - System Update Utility

### Overview

`update-system.bash` is a shell script designed to simplify the process of updating system packages on Debian-based Linux distributions (e.g., Ubuntu). It automates common update commands.

### Prerequisites

*   **Operating System:** A Debian-based Linux distribution (e.g., Ubuntu, Debian).
*   **Permissions:** You will likely need `sudo` (superuser) privileges to execute this script successfully, as package management commands typically require root access.

### Usage

1.  Navigate to the directory containing the script.
2.  Make sure the script is executable:
    ```bash
    chmod +x update-system.bash
    ```
3.  Run the script, preferably with `sudo`:
    ```bash
    sudo ./update-system.bash
    ```

### Script Actions

The script performs the following actions:
*   `apt-get clean`: Clears out the local repository of retrieved package files.
*   `apt-get update -y`: Resynchronizes the package index files from their sources.
*   `apt-get upgrade -y`: Installs the newest versions of all packages currently installed on the system.
*   `apt-get dist-upgrade -y`: In addition to performing the function of upgrade, this also intelligently handles changing dependencies with new versions of packages.
*   `apt autoremove -y`: Removes packages that were automatically installed to satisfy dependencies for other packages and are now no longer needed.
*   Finally, it displays the content of `/var/run/reboot-required` to inform you if a system reboot is necessary after the updates.
```

---

## Future Improvements

This README can be further enhanced with the following sections:

*   **Contributing:** Guidelines for how others can contribute to these scripts or add new ones. This might include coding standards, testing procedures, or how to propose changes.
*   **License:** Information about the licensing terms under which these scripts are provided (e.g., MIT, GPL, etc.). This is important for users to understand how they can use or modify the scripts.
```
