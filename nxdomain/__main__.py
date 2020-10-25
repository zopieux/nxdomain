import argparse
import logging
import sys

from nxdomain import (
    BindGenerator,
    BlockList,
    BlockListGenerator,
    BlockListType,
    DnsmasqGenerator,
    download_and_generate,
)


def main(argv):
    p = argparse.ArgumentParser(description="nxdomain -- domain block list management")
    p.add_argument("--out", required=True, help="output zone filename")
    p.add_argument(
        "--format",
        required=True,
        choices=["bind", "dnsmasq"],
        help="output format, BIND zone file or dnsmasq config",
    )
    p.add_argument("--simple", action="append", help="adds a simple block list URI")
    p.add_argument(
        "--hosts",
        action="append",
        help="adds a 'hosts' syntax block list URI",
    )
    args = p.parse_args(argv)

    simple_lists = [BlockList(uri, BlockListType.simple) for uri in (args.simple or [])]
    hosts_lists = [BlockList(uri, BlockListType.hosts) for uri in (args.hosts or [])]
    all_lists = simple_lists + hosts_lists

    if not all_lists:
        p.error("at least one --simple or --hosts is required")
        # Exits.

    generator: BlockListGenerator
    if args.format == "bind":
        generator = BindGenerator()
    elif args.format == "dnsmasq":
        generator = DnsmasqGenerator()

    logging.basicConfig(level=logging.INFO)
    download_and_generate(all_lists, generator, args.out)


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
