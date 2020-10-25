# nxdomain
 
[![Build status](https://github.com/Zopieux/nxdomain/workflows/Test%20and%20package/badge.svg)](https://github.com/Zopieux/nxdomain/actions)

A domain (ad) block list creator. Takes block lists from local files or URLs as input
(in `hosts(5)` or domain-list format) and outputs a BIND zone or dnsmasq config.

### Sample usage

```shell
$ python -m nxdomain \
    # Where to store the output file.
    --out=adblock.zone \
    # BIND Response Policy Zone file. Also available: --format=dnsmasq.
    --format=bind \
    # A simple list of domains, one per line. Lines starting with '#' are skipped.
    --simple=https://mirror1.malwaredomains.com/files/justdomains \
    # A hosts(5) formatted list of domains. Lines starting with '#' are skipped.
    --hosts=https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
```

### Notes

This program does not try to be smart. Reloading the DNS server is your responsibility. There is no caching or smart diffing.
The only smartness is that, with `--format=bind`, the SOA serial will be incremented automatically if the file already exists. 

### License

GNU General Public License v3.0
