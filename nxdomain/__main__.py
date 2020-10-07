import argparse
import logging

from nxdomain import (
    BlockList,
    BlockListType,
    DnsmasqGenerator,
    BindGenerator,
    download_and_generate,
    BlockListGenerator,
)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="nxdomain -- domain block list management")
    p.add_argument("--out", required=True, help="output zone filename")
    p.add_argument(
        "--format",
        required=True,
        choices=["bind", "dnsmasq"],
        help="output format, BIND zone file or dnsmasq config",
    )
    p.add_argument(
        "--simple", nargs="?", action="append", help="adds a simple block list URI"
    )
    p.add_argument(
        "--hosts",
        nargs="?",
        action="append",
        help="adds a 'hosts' syntax block list URI",
    )
    args = p.parse_args()

    simple_lists = [BlockList(uri, BlockListType.simple) for uri in args.simple]
    hosts_lists = [BlockList(uri, BlockListType.hosts) for uri in args.hosts]
    all_lists = simple_lists + hosts_lists

    if not all_lists:
        p.error("at least one --simple or --hosts is required")
        # (sys.exist)

    generator: BlockListGenerator
    if args.format == "bind":
        generator = BindGenerator()
    elif args.format == "dnsmasq":
        generator = DnsmasqGenerator()
    else:
        p.error("unknown output format")
        # (sys.exist)

    logging.basicConfig(level=logging.INFO)
    download_and_generate(all_lists, generator, args.out)
