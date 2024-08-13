#!/bin/env python3
import json
import os
import tempfile
import urllib.request

PASSWORD = ''
ELDEN_RING_PATH = '~/.steam/steam/steamapps/common/ELDEN RING/Game'


_ELDEN_RING_PATH = os.path.expanduser(ELDEN_RING_PATH)
_MOD_VERSION_PATH = os.path.join(_ELDEN_RING_PATH, 'SeamlessCoop.version')


def get_current_version() -> str | None:
    try:
        with open(os.path.expanduser(_MOD_VERSION_PATH)) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def get_latest_version_info() -> tuple[dict, str]:
    response = urllib.request.urlopen('https://api.github.com/repos/LukeYui/EldenRingSeamlessCoopRelease/releases')

    try:
        releases = json.load(response)
    except Exception as e:
        raise RuntimeError(f'Failed to get releases from GitHub: {type(e)}, {e}') from e

    if not releases:
        raise RuntimeError('Got empty releases response')

    latest_release = releases[0]

    latest_assets = latest_release.get('assets', [])
    if not latest_assets:
        raise RuntimeError(f'Latest release has empty assets: {releases}')

    if len(latest_assets) > 1:
        raise RuntimeError(f'Latest release has more than one asset: {latest_assets}')

    latest_url = latest_assets[0].get('browser_download_url')
    if not latest_url:
        raise RuntimeError(f'Latest release has no download url: {latest_assets}')

    return latest_release, latest_url



def update_to(
    url: str,
    version: str,
    version_name: str,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, 'archive.zip')
        uncompressed_path = os.path.join(tmpdir, 'dir')
        config_path = os.path.join(uncompressed_path, 'SeamlessCoop', 'ersc_settings.ini')

        os.system(f'''
            (wget {url} -O {archive_path} && \
            unzip {archive_path} -d {uncompressed_path} && \
            sed -i {config_path} -e 's/cooppassword =.*/cooppassword = {PASSWORD}/g' \
              {config_path} && \
            cp -r {uncompressed_path}/* {_ELDEN_RING_PATH}) >/dev/null 2>&1 && \
            echo '{version}' > {_MOD_VERSION_PATH} && \
            echo 'Updated to {version_name}'
        ''')


def main():
    latest_release, latest_url = get_latest_version_info()

    current_version = get_current_version()
    latest_version = latest_release['created_at']
    latest_version_name = latest_release['name']
    if current_version == latest_version:
        print('Already at the latest version', latest_version_name, 'dated', current_version)
        return

    update_to(
        url=latest_url,
        version=latest_version,
        version_name=latest_version_name,
    )

if __name__ == '__main__':
    main()
