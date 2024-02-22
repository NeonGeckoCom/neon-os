# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from os.path import join
from sys import argv
from os import walk, listdir, makedirs
from pprint import pprint
from shutil import move


def get_image_dirs(base_dir: str) -> dict:
    """
    Get a dict of stable images, beta images, and update file directories
    :param base_dir: Root directory to search for Neon OS files
    :return: dict of stable, beta, and updates (beta and stable)
    """
    directories = {"stable": [],
                   "beta": [],
                   "updates": {"stable": [],
                               "beta": []}}
    for root, dirs, files in walk(base_dir):
        for d in dirs:
            if "updates" in root:
                if "dev" in d:
                    directories['updates']["beta"].append(join(root, d))
                elif "master" in d:
                    directories['updates']["stable"].append(join(root, d))
            elif "dev" in d:
                directories['beta'].append(join(root, d))
            elif "master" in d:
                directories['stable'].append(join(root, d))
    return directories


def prune_directory(directory: str, releases_to_keep: int,
                    archive: str):
    print(directory)
    if "/updates/" in directory:
        # Updates directories contain json and squashfs files
        releases_to_keep = 2 * releases_to_keep

    releases = listdir(directory)
    releases.sort()
    files_to_keep = releases[-releases_to_keep:]
    for file in releases:
        if file in files_to_keep:
            print(f"Keep: {file}")
        else:
            print(f"Archive: {file}")
            move(join(directory, file), join(archive, file))


def prune_uploaded_images(base_dir: str, archive: str):
    dirs = get_image_dirs(base_dir)
    pprint(dirs)
    makedirs(archive_dir, exist_ok=True)
    for group in (dirs['beta'], dirs['stable'],
                  dirs['updates']['beta'], dirs['updates']['stable']):
        for d in group:
            if "dev" in d:
                releases_to_keep = 3
            else:
                releases_to_keep = 5
            prune_directory(d, releases_to_keep, archive)


if __name__ == "__main__":
    root_dir = argv[1]  # /var/www/html/app/files/neon_images
    archive_dir = argv[2]  # /home/d_mcknight/image_archives
    prune_uploaded_images(root_dir, archive_dir)
