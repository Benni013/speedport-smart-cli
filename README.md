# speedport-smart-cli
Command Line Interface for the hidden menu in the Speedport Smart 1st Gen

### Requirements:
* Python version 3.6 or newer
#### Python libraries:
* requests

### Usage:
`./speedport-hidden.py [OPTIONS]`

| option (short) | option (long)         | description                                                      |
|----------------|-----------------------|------------------------------------------------------------------|
|  `-h`          |  `--help`             | print help message                                               |
|  `-v`          |  `--version`          | print program's version number                                   |
|  `-u`          |  `--url URL`          | set your Speedport URL                                           |
|  `-d`          |  `--dynamic`          | set dynamic mode (refreshes data at given time interval)         |
|  `-r`          |  `--refresh REFRESH`  | set refresh rate in dynamic mode in seconds (default=10, min=4)  |
|                |  `--memcpu`           | print utilization information                                    |
|                |  `--dev`              | print interface information                                      |
|                |  `--wifi`             | print Wi-Fi information                                          |
|                |  `--dsl`              | print DSL information                                            |
|                |  `--arp`              | print ARP table information                                      |
|                |  `--all`              | print all information                                            |
