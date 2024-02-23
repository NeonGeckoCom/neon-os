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

import yaml
import json

from sys import argv
from os import listdir, remove
from os.path import dirname, join, isfile
from typing import List, Dict
from datetime import datetime


def get_new_builds() -> List[dict]:
    """
    Get build info for all new builds completed during automation
    :return: list of build metadata
    """
    base_dir = dirname(dirname(__file__))
    builds = list()
    for file in listdir(base_dir):
        if not file.endswith(".json"):
            continue
        with open(join(base_dir, file)) as f:
            builds.append(json.load(f))
        remove(join(base_dir, file))
    return builds


def parse_builds_into_metadata(builds: List[dict]) -> Dict[str, dict]:
    """
    Parse a list of build specs into dict metadata per-image name (core+platform)
    :param builds: List of build specs from `get_new_builds`
    :return: dict metadata for all specified builds
    """
    build_meta = dict()
    for build in builds:
        build_meta[build['base_os']['name']] = build
    return build_meta


def update_build_indices(beta: bool) -> List[dict]:
    """
    Build or update yaml indices for any new builds
    @param beta: If true, newly added builds are beta
    """
    new_meta = parse_builds_into_metadata(get_new_builds())
    base_dir = dirname(dirname(__file__))
    new_images = list()
    all_meta_file = join(base_dir, f"all.yaml")
    if isfile(all_meta_file):
        with open(all_meta_file) as f:
            all_meta = yaml.safe_load(f)
    else:
        all_meta = list()

    for key, val in new_meta.items():
        meta_file = join(base_dir, f"{key}.yaml")
        if isfile(meta_file):
            with open(meta_file) as f:
                meta = yaml.safe_load(f)
        else:
            meta = list()

        # Determine new version
        val["version"] = datetime.fromtimestamp(
            val["base_os"]["time"]).strftime("%y.%m.%d")
        if beta and meta and "b" in meta[0]["version"]:
            new_beta = int(meta[0]["version"].split("b")) + 1
            val["version"] = f'{val["version"]}b{new_beta}'
        elif beta:
            val["version"] = f'{val["version"]}b1'

        # Add new builds to the top of the list
        meta.insert(0, val)
        all_meta.insert(0, val)
        new_images.append({"image": val['base_os']['name'],
                           "version": val["version"],
                           "download": val['download_url']})

        with open(meta_file, 'w') as f:
            yaml.safe_dump(meta, f)

    with open(all_meta_file, 'w') as f:
        yaml.safe_dump(all_meta, f)

    return new_images


def write_changelog(new_images: List[dict]):
    release_notes = join(dirname(dirname(__file__)), "release_notes.md")
    if isfile(release_notes):
        with open(release_notes, 'r') as f:
            content = f.readlines()
        old_version = [line for line in content if
                       line.startswith("tag")][0].split('=')[1].strip()
    else:
        old_version = None
    date_ver = new_images[0]['version']
    beta = False
    if 'b' in date_ver:
        date_ver = date_ver.split('b')[0]
        if date_ver in old_version and "beta" in old_version:
            try:
                beta = int(old_version.split('beta')[1]) + 1
            except Exception as e:
                print(e)
                beta = 1

    title = f"# Neon OS Beta Release {date_ver}" if beta else \
        f"# Neon OS Release {date_ver}"
    tag = f"{date_ver}.beta{beta}" if beta else date_ver

    release_strings = [(f"[{image['image']} {image['version']}]"
                        f"({image['download']})\n") for image in new_images]
    with open(release_notes, 'w') as f:
        f.writelines([f"{title}\n",
                      "This is an automated release\n",
                      f"tag={tag}\n",
                      "\n## Release Images"] +
                     release_strings)


if __name__ == "__main__":
    is_beta = argv[1] == "dev"
    images = update_build_indices(is_beta)
    write_changelog(images)
