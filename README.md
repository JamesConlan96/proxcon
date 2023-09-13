# Proxcon

A utility for quickly switching proxychains proxies

## Usage

**proxcon.py**

```
usage: proxcon.py [-h] {switch,add,update,list,active,delete} ...

positional arguments:
  {switch,add,update,list,active,delete}
    switch              switch to a proxy definition
    add                 add a proxy definition
    update              update a proxy definition
    list                list all proxy definitions
    active              show active proxy definition
    delete              delete a proxy definition

options:
  -h, --help            show this help message and exit
```

**proxcon.py switch**

Switch to a proxy definition

```
usage: proxcon.py switch [-h] [-f FILE] name

positional arguments:
  name                  name of proxy definition

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  proxychains configuration file to use (default: '/etc/proxychains4.conf')
```

**proxcon.py add**

Add a proxy definition

```
usage: proxcon.py add [-h] -t {http,raw,socks4,socks5} -i IPV4 -p PORT [-u USER] [-P] name

positional arguments:
  name                  name of proxy definition

options:
  -h, --help            show this help message and exit
  -t {http,raw,socks4,socks5}, --type {http,raw,socks4,socks5}
                        proxy type
  -i IPV4, --ipv4 IPV4  proxy server IPv4 address
  -p PORT, --port PORT  proxy server port
  -u USER, --user USER  username for proxy authentication
  -P, --pass            a password is required to access the proxy
```

**proxcon.py update**

Update a proxy definition

```
usage: proxcon.py update [-h] [-r RENAME] [-t {http,raw,socks4,socks5}] [-i IPV4] [-p PORT] [-u USER] [-P] name

positional arguments:
  name                  name of proxy definition

options:
  -h, --help            show this help message and exit
  -r RENAME, --rename RENAME
                        new name for proxy definition
  -t {http,raw,socks4,socks5}, --type {http,raw,socks4,socks5}
                        proxy type
  -i IPV4, --ipv4 IPV4  proxy server IPv4 address
  -p PORT, --port PORT  proxy server port
  -u USER, --user USER  username for proxy authentication
  -P, --pass            a password is required to access the proxy
```

**proxcon.py list**

List all proxy definitions

```
usage: proxcon.py list [-h]

options:
  -h, --help  show this help message and exit
```

**proxcon.py active**

Show active proxy definition

```
usage: proxcon.py active [-h] [-f FILE]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  proxychains configuration file to use (default: '/etc/proxychains4.conf')
```

**proxcon.py delete**

Delete a proxy definition

```
usage: proxcon.py delete [-h] name

positional arguments:
  name        name of proxy definition

options:
  -h, --help  show this help message and exit
```

## Requirements

All requirements can be installed by running the following command from within the proxconf directory:

```
pip install -r requirements.txt
```
