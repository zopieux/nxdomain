import abc
import enum
import itertools
import logging
import re
import urllib.request
from typing import Iterable, BinaryIO, NamedTuple, List

import dns.zone  # type: ignore

# Certainly not spec-compliant, but good enough for sanity checks.
DOMAIN_NAME_REGEXP = re.compile(
    r"\b((?:(?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,63})\b"
)
HOSTS_REGEXP = re.compile(r"^\S+\s+(.+)$")


class BlockListType(enum.Enum):
    simple = "simple"
    hosts = "hosts"


class BlockList(NamedTuple):
    uri: str
    type: BlockListType


class BlockListGenerator(abc.ABC):
    def generate(self, domains: Iterable[str], filename: str):
        ...  # pragma: no cover


class DnsmasqGenerator(BlockListGenerator):
    def generate(self, domains: Iterable[str], filename: str):
        domains = sorted(set(domains))

        with open(filename, "w") as f:
            for domain in domains:
                f.write(f"address=/{domain}/#\n")

        logging.info("block list has %d domains", len(domains))


class BindGenerator(BlockListGenerator):
    def generate(self, domains: Iterable[str], filename: str):
        ttl = 3600
        origin = "rpz.local"

        def read_header():
            with open(filename, "r") as f:
                for line in f:
                    if not line.startswith("@"):
                        break
                    yield line

        try:
            # Read "header" only since it's expensive to parse everything.
            zone = dns.zone.from_text("\n".join(read_header()), origin=origin)
        except (dns.exception.DNSException, IOError):
            zone = dns.zone.Zone(origin)

        existing_soa_set = zone.get_rdataset("@", "SOA")
        zone.nodes.clear()

        soa_set = zone.find_rdataset("@", "SOA", create=True)
        if existing_soa_set is None:
            soa_set.ttl = 3600
            soa_set.add(
                dns.rdata.from_text(
                    "IN", "SOA", "@ hostmaster 0 86400 7200 2592000 86400"
                )
            )
            logging.info("creating zone from scratch")
        else:
            soa_set.update(existing_soa_set)
            # Increment serial.
            serial = soa_set[0].serial + 1
            soa_set.add(soa_set[0].replace(serial=serial))
            logging.info("parsed existing header, new serial is %d", serial)

        in_ns = zone.find_rdataset("@", "NS", create=True)
        in_ns.ttl = ttl
        in_ns.add(dns.rdata.from_text("IN", "NS", "LOCALHOST."))

        in_cname_dot = dns.rdataset.from_text("IN", "CNAME", ttl, ".")
        for domain in domains:
            zone.find_node(domain, create=True).replace_rdataset(in_cname_dot)

        zone.to_file(filename, sorted=True)
        logging.info("block list has %d domains", len(zone.nodes) - 1)


def parse_block_list(list_type: BlockListType, f: BinaryIO) -> Iterable[str]:
    def reader():
        for raw_line in f:
            line = raw_line.decode().strip()
            if not line:
                continue
            if list_type is BlockListType.hosts:
                if (match := HOSTS_REGEXP.match(line)) is not None and (
                    domain := match.group(1).strip()
                ):
                    yield domain
            elif list_type is BlockListType.simple:
                if not line.startswith("#"):
                    yield line
            else:  # pragma: no cover
                raise ValueError(f"unsupported list type {list_type}")

    for line in reader():
        if (m := DOMAIN_NAME_REGEXP.search(line)) is not None and (
            domain := m.group(1).strip()
        ):
            try:
                # Validate syntax and yield.
                yield dns.name.from_text(domain).to_text(omit_final_dot=True)
            except dns.exception.DNSException:  # pragma: no cover
                pass


def read_block_list(block_list: BlockList) -> Iterable[str]:
    if block_list.uri.startswith("http"):
        with urllib.request.urlopen(block_list.uri, timeout=10) as r:
            yield from parse_block_list(block_list.type, r)
            return

    with open(block_list.uri, "rb") as f:
        yield from parse_block_list(block_list.type, f)
        return


def download_and_generate(
    lists: List[BlockList], generator: BlockListGenerator, filename: str
):
    domains = itertools.chain(*(read_block_list(block_list) for block_list in lists))
    generator.generate(domains, filename)
