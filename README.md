# Netgraph Template Generator

**This project is collaborate with [Netgraph](https://github.com/leo900807/netgraph).**

## Installation

**Please setup MRTG first, see [MRTG Installation](#mrtg-installation) to get more information.**

#### 1. Clone netgraph template generator

```bash
$ git clone https://github.com/leo900807/netgraph-template-generator
$ cd netgraph-template-generator
```

#### 2. Edit environment variables

Copy `config.ini.sample` to `config.ini` and edit variable values.  
Copy `current_flow.sh.sample` to `current_flow.sh` and change value of `SCRIPT_PATH` to this directory.

#### 3. Set cronjob

Add `current_flow.sh` into cronjob.

## MRTG Installation

### Installation

```bash
sudo apt-get install mrtg -y
```

### MRTG configuration

#### 1. Create MRTG working directories

```bash
sudo mkdir /var/www/mrtg
sudo mkdir /etc/mrtg
```

#### 2. Generate config files by cfgmaker

```bash
sudo cfgmaker --output=/etc/mrtg/DESIRED_CONFIG_NAME.cfg NETWORK_DEVICE_COMMUNITY@NETWORK_DEVICE_IP --snmp-options=:::::SNMP_VERSION --global "WorkDir: /var/www/mrtg/" --global "RunAsDaemon: yes" --global "Options[_]: growright"
```

#### 3. Aggregate config files into a single file:

1. Create and Edit `mrtg.cfg`

```bash
vim /etc/mrtg/mrtg.cfg
```

2. Include other config files in `mrtg.cfg` like this:

```bash
Include: CONFIG_FILE_1.cfg
Include: CONFIG_FILE_2.cfg
...
```

#### 4. Run MRTG

```bash
sudo env LANG=C /usr/bin/mrtg /etc/mrtg/mrtg.cfg
```

You may have to execute the command until there're no error messages (typically three times).

#### 5. Generate index page by indexmaker

```bash
sudo indexmaker --perhost --output=/var/www/mrtg/index.html /etc/mrtg/mrtg.cfg
```
