#!/bin/bash
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

debos_dir=${1}  # Absolute path to already cloned neon_debos
repo_ref=${2}  # dev, master
recipe=${3}  # debian-neon-image.yml, debian-node-image.yml
platforms=${4}  # "rpi4 opi5"
output_dir=${5}  # /var/www/html/app/files/neon_images
base_url=${6}  # https://2222.us
os_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
timestamp=$(date '+%Y-%m-%d_%H_%M')
mem_limit=${MEM_LIMIT:-"32G"}
core_limit=${CORE_LIMIT:-8}

debos_version="$(python3 "${debos_dir}/version.py")"

[ -d "${debos_dir}/output" ] || mkdir "${debos_dir}/output"
echo "Building recipe with core=${repo_ref} recipe=${debos_version}"
chmod ugo+x "${debos_dir}/scripts/"*

for platform in ${platforms}; do
  image_id="${recipe%.*}-${platform}_${timestamp}"
  build_version=$(python3 "${os_dir}/scripts/get_build_version.py" "${recipe%.*}" "${platform}" "${repo_ref}" "${timestamp}")
  # TODO: Refactor builds to be platform-specific and not device-specific
  if [ "${platform}" == "rpi4" ]; then
    device="mark_2"
    kernel_version="6.1.77-gecko+"
  else
    device="${platform}"
    kernel_version="5.10.110-gecko+"
  fi
  docker run --rm \
  --device /dev/kvm \
  --workdir /image_build \
  --mount type=bind,source="${debos_dir}",destination=/image_build \
  --group-add=108 \
  --security-opt label=disable \
  --name neon_debos_ghaction \
  godebos/debos "${recipe}" \
  -t platform:"${platform}" \
  -t device:"${device}" \
  -t kernel_version:"${kernel_version}" \
  -t architecture:arm64 \
  -t image:"${image_id}" \
  -t neon_core:"${repo_ref}" \
  -t neon_debos:"${debos_version}" \
  -t build_version:"${build_version}" \
  -t build_cores:"${core_limit}" -m "${mem_limit}" -c "${core_limit}" || exit 2
  echo "Completed build: ${platform}"

  # Determine Server Path for outputs
  output_path="${output_dir}/${platform}/"
  update_path="${output_dir}/${platform}/updates/"
  if [[ "${recipe}" == *node* ]]; then
    output_path="${output_dir}/node/${platform}/"
    update_path="${output_dir}/node/${platform}/updates/"
  elif [[ "${recipe}" == *neon* ]]; then
    output_path="${output_dir}/core/${platform}/"
    update_path="${output_dir}/core/${platform}/updates/"
  fi

  # Ensure directories exist
  [ -d "${output_path}${repo_ref}" ] || mkdir -p "${output_path}${repo_ref}"
  [ -d "${update_path}${repo_ref}" ] || mkdir -p "${update_path}${repo_ref}"

  # Add `download_url` metadata to json output
  url="${base_url}$(sed -e "s|^/var/www/html||g" <<< "${output_path}")${repo_ref}/${image_id}.img.xz"
  sed -i -e "s|^{|{\n  \"download_url\": \"${url}\",|g" "${debos_dir}/output/"*.json
  cp "${debos_dir}/output/${image_id}.json" "${os_dir}"  # Copy metadata for upload/parse
  mv "${debos_dir}/output/${image_id}.img.xz" "${output_path}${repo_ref}/"  # Image File
  mv "${debos_dir}/output/${image_id}.squashfs" "${update_path}${repo_ref}/"  # Update File
  mv "${debos_dir}/output/${image_id}.json" "${update_path}${repo_ref}/"  # Update Metadata
done

echo "completed ${timestamp}"
