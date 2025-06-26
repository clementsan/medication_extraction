"""
Testing module on CLI
"""

from typer.testing import CliRunner
from medication_extraction.main import app


runner = CliRunner()


def test_extract():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
