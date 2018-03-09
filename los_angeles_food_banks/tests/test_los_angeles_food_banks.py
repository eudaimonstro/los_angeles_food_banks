#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `los_angeles_food_banks` package."""


import unittest
from click.testing import CliRunner

from los_angeles_food_banks import los_angeles_food_banks
from los_angeles_food_banks import cli


class TestLos_angeles_food_banks(unittest.TestCase):
    """Tests for `los_angeles_food_banks` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'los_angeles_food_banks.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
