from unittest import mock

from nxdomain import (
    read_block_list,
    BlockList,
    BlockListType,
    download_and_generate,
    DnsmasqGenerator,
    BindGenerator,
)


def test_read_simple(testdir):
    f = BlockList(str(testdir / "simple.txt"), BlockListType.simple)
    bl = list(read_block_list(f))

    assert len(bl) == 3
    assert set(bl) == {"example.org", "example.com", "example.net"}


def test_read_hosts(testdir):
    f = BlockList(str(testdir / "hosts.txt"), BlockListType.hosts)
    bl = list(read_block_list(f))

    assert len(bl) == 4
    assert set(bl) == {"example.org", "example.com"}


def test_read_http(testdir):
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value = (testdir / "simple.txt").open("rb")
        f = BlockList("http://example.org/simple.txt", BlockListType.simple)
        bl = list(read_block_list(f))

        assert len(bl) == 3
        assert set(bl) == {"example.org", "example.com", "example.net"}


def test_generate_dnsmasq(testdir, tmp_path):
    bls = [BlockList(str(testdir / "simple.txt"), BlockListType.simple)]
    generator = DnsmasqGenerator()
    out_path = tmp_path / "out.conf"
    download_and_generate(bls, generator, str(out_path))

    assert out_path.open().read() == "\n".join(
        [
            "address=/example.com/#",
            "address=/example.net/#",
            "address=/example.org/#",
            "",
        ]
    )


def test_generate_bind(testdir, tmp_path):
    bls = [BlockList(str(testdir / "simple.txt"), BlockListType.simple)]
    generator = BindGenerator()
    out_path = tmp_path / "out.zone"
    download_and_generate(bls, generator, str(out_path))

    assert (
        out_path.open().read()
        == """@ 3600 IN SOA @ hostmaster 0 86400 7200 2592000 86400
@ 3600 IN NS LOCALHOST.
example.com 3600 IN CNAME .
example.net 3600 IN CNAME .
example.org 3600 IN CNAME .
"""
    )

    download_and_generate(bls, generator, str(out_path))
    assert "hostmaster 1" in out_path.open().readline()
