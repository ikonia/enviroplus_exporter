#!/usr/bin/env python3
"""Rebuild vendor/ from hash-pinned PyPI wheels (standard library only).

Usage: python3 vendor/fetch.py            # rewrites vendor/exporter, vendor/lcd, vendor/licenses
To bump a library: change VERSION and SHA256 here (take the sha256 from the PyPI release page),
run the script, review `git diff vendor/`, and update VENDORED.md.
Only pure-Python wheels are used; nothing from a wheel is executed.
"""
import hashlib
import io
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "https://files.pythonhosted.org/packages/py3/{0}/{1}/{2}"

# name: (wheel filename, sha256, [(path inside wheel, destination under vendor/)], licence path inside wheel)
LIBS = {
    "ads1015": ("ads1015-1.0.0-py3-none-any.whl", "3497a7457f045b4abd049e96ab3a5ff95603a3b08b36273e4dfa6234964130df",
                [("ads1015/", "exporter/ads1015/")], "ads1015-1.0.0.dist-info/licenses/LICENSE"),
    "i2cdevice": ("i2cdevice-1.0.0-py3-none-any.whl", "595cfa3815aab4d8a4bbe1cbd4a4e1271d56cf7c1de367eab6a94dd80566f0c1",
                  [("i2cdevice/", "exporter/i2cdevice/")], "i2cdevice-1.0.0.dist-info/licenses/LICENSE"),
    "ltr559": ("ltr559-1.0.0-py3-none-any.whl", "0805f2d9ab43b2f622847ec71cb6fbca2b91b396aafb121d911172a366a56c3d",
               [("ltr559/", "exporter/ltr559/")], "ltr559-1.0.0.dist-info/licenses/LICENSE"),
    "pimoroni-bme280": ("pimoroni_bme280-1.0.0-py3-none-any.whl", "7415a037ba3dd14ce40d705bb006e02f53b276c72aef75fda5ea86daef666a4f",
                        [("bme280/", "exporter/bme280/")], "pimoroni_bme280-1.0.0.dist-info/licenses/LICENSE"),
    "pms5003": ("pms5003-1.0.1-py3-none-any.whl", "38f51a40d1a09efb4bb7f6f01376dc870ed720253a664a1f4d1ae19581f6e3db",
                [("pms5003/", "exporter/pms5003/")], "pms5003-1.0.1.dist-info/licenses/LICENSE"),
    "gpiodevice": ("gpiodevice-0.0.5-py3-none-any.whl", "b808250cd1d89379b69f98cc6442b6b098aa32604c3ed7fb194a39607ee35253",
                   [("gpiodevice/", "exporter/gpiodevice/")], "gpiodevice-0.0.5.dist-info/licenses/LICENSE"),
    # enviroplus: only the MICS6814 gas reader is needed. noise.py pulls in sounddevice/numpy and is left out.
    "enviroplus": ("enviroplus-1.0.2-py3-none-any.whl", "e3e862f08554f89183ea419c072b4a8647d69cc8dd256579453f4b38076edd04",
                   [("enviroplus/__init__.py", "exporter/enviroplus/__init__.py"), ("enviroplus/gas.py", "exporter/enviroplus/gas.py")],
                   "enviroplus-1.0.2.dist-info/licenses/LICENSE"),
    # st7735 is only for the optional enviroplus-lcd package. The ST7735.py shim is left out.
    "st7735": ("st7735-1.0.0-py3-none-any.whl", "20eb580e3d2462d8498ea5922cb5c1128abc46cbbc91998f07911054b3594f83",
               [("st7735/", "lcd/st7735/")], "st7735-1.0.0.dist-info/licenses/LICENSE"),
}


def wheel_url(name, filename):
    import json
    version = filename.split("-")[1]
    meta = json.load(urllib.request.urlopen("https://pypi.org/pypi/{}/{}/json".format(name, version), timeout=30))
    for f in meta["urls"]:
        if f["filename"] == filename:
            return f["url"]
    raise SystemExit("wheel {} not found on PyPI".format(filename))


def main():
    for sub in ("exporter", "lcd", "licenses"):
        shutil.rmtree(HERE / sub, ignore_errors=True)
    for name, (filename, sha256, files, licence) in LIBS.items():
        data = urllib.request.urlopen(wheel_url(name, filename), timeout=60).read()
        if hashlib.sha256(data).hexdigest() != sha256:
            raise SystemExit("sha256 mismatch for {}: refusing to continue".format(filename))
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = z.namelist()
            for src, dst in files:
                for member in names:
                    if member == src or (src.endswith("/") and member.startswith(src)):
                        if member.endswith("/") or "__pycache__" in member:
                            continue
                        out = HERE / (dst + member[len(src):] if src.endswith("/") else dst)
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_bytes(z.read(member))
            (HERE / "licenses").mkdir(exist_ok=True)
            (HERE / "licenses" / (name + ".LICENSE")).write_bytes(z.read(licence))
        print("vendored", filename)


if __name__ == "__main__":
    sys.exit(main())
