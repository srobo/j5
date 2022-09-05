"""Tests for the SRv4 serial protocol."""
import pytest

from j5.backends.hardware.sr.v4.serial.protocol import (
    SRV4SerialProtocolBackend,
)


class TestParseVersion:
    """Test that we can parse the version."""

    @pytest.mark.parametrize(
        "version_string,hw,major,minor",
        [
            ("4.4", 4, 4, 0),
            ("4.4.0", 4, 4, 0),
            ("4.4.4", 4, 4, 4),
            ("12.0", 12, 0, 0),
            ("12.34.56", 12, 34, 56),
        ],
    )
    def test_parse_version_string(
        self,
        version_string: str,
        hw: int,
        major: int,
        minor: int,
    ) -> None:
        """Test that we can parse the version string."""
        version = SRV4SerialProtocolBackend._parse_version_string(version_string)
        assert version.hw_ver == hw
        assert version.fw_major == major
        assert version.fw_minor == minor
