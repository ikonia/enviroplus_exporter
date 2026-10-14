# Vendored libraries

Pure-Python Pimoroni libraries that Debian does not package. Each is taken unmodified from a PyPI wheel
pinned by sha256 in `fetch.py`. They install to `/usr/lib/enviroplus/` (a private directory, not on the
system Python path), so they cannot clash with a system or pip-installed copy.

| library | version | used by | licence | notes |
|---|---|---|---|---|
| ads1015 | 1.0.0 | exporter | MIT, Pimoroni | MICS6814 ADC |
| i2cdevice | 1.0.0 | exporter | MIT, Pimoroni | needs system `python3-smbus2` |
| ltr559 | 1.0.0 | exporter | MIT, Pimoroni | light and proximity |
| pimoroni-bme280 | 1.0.0 | exporter | MIT, Pimoroni | module name `bme280` |
| pms5003 | 1.0.1 | exporter | MIT, Pimoroni | needs system `python3-serial`, `python3-libgpiod` |
| gpiodevice | 0.0.5 | exporter, lcd | MIT, Pimoroni | the version running on the nodes; 0.1.0 exists but is untested here |
| enviroplus | 1.0.2 | exporter | MIT, Pimoroni | only `gas.py`; `noise.py` (sounddevice, numpy, microphone) left out |
| st7735 | 1.0.0 | lcd | MIT, Adafruit and Pimoroni | needs system `python3-numpy`, `python3-spidev`; `ST7735.py` shim left out |

System (Debian trixie) dependencies, not vendored: `python3-libgpiod` (module `gpiod`, v2 API),
`python3-smbus2`, `python3-serial`, `python3-prometheus-client`; LCD only: `python3-numpy`, `python3-pil`,
`python3-spidev`, `fonts-roboto`.

Licence texts are in `licenses/` and are installed under `/usr/share/doc/<package>/`.
To refresh: `python3 vendor/fetch.py`, review `git diff vendor/`, then update this table.
