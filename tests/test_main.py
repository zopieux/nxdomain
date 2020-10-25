import pytest

from nxdomain.__main__ import main


def test_no_list(capsys):
    with pytest.raises(SystemExit):
        main(["--out", "foo", "--format", "dnsmasq"])
    assert "at least one" in capsys.readouterr().err


def test_no_format(capsys):
    with pytest.raises(SystemExit):
        main(["--out", "foo", "--simple", "dummy.list"])
    assert "--format" in capsys.readouterr().err


def test_no_out(capsys):
    with pytest.raises(SystemExit):
        main(["--format", "dnsmasq", "--simple", "dummy.list"])
    assert "--out" in capsys.readouterr().err


@pytest.mark.parametrize(
    "in_param", [("--simple", "simple.txt"), ("--hosts", "hosts.txt")]
)
@pytest.mark.parametrize("out_format", ["dnsmasq", "bind"])
def test_simple(in_param, out_format, testdir, tmp_path):
    in_flag, in_name = in_param
    in_path = str(testdir / in_name)
    out = tmp_path / "out.conf"

    main(["--out", str(out), in_flag, in_path, "--format", out_format])
    assert out.stat().st_size > 0
