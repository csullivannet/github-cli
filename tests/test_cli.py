"""
Tests for cli.py
"""

import argparse
import datetime
import pytest
from pytest_mock import mocker
import requests
import requests_mock
from cli import cli

MOCK_URL = "https://api.github.com/repos/mock/mock/"
MOCK_PRS = [
    {
        "url": "https://api.github.com/repos/mock/mock/pulls/1",
        "owner": "mock1",
        "created_at": "2021-01-30T12:13:14Z",
        "labels": [
            {"name": "mock_label1"},
            {"name": "mock_label2"},
            {"name": "mock_label3"},
        ],
    },
    {
        "url": "https://api.github.com/repos/mock/mock/pulls/2",
        "owner": "mock2",
        "created_at": "2021-02-30T12:13:14Z",
        "labels": [{"name": "mock_label1"}],
    },
    {
        "url": "https://api.github.com/repos/mock/mock/pulls/3",
        "owner": "mock1",
        "created_at": "2021-03-30T12:13:14Z",
        "labels": [{"name": "mock_label1"}, {"name": "mock_label3"}],
    },
]


def test_max_age_no_label(requests_mock, mocker, capsys):
    args = argparse.Namespace(
        repo=["mock"],
        org="mock",
        max_age="5",
        labels=None,
        all_labels=False,
        file=None,
        verbose=False,
    )
    mocker.patch("cli.arguments", return_value=args)
    mocker.patch("cli.get_now", return_value=datetime.date(2021, 4, 1))
    requests_mock.get(MOCK_URL, json=MOCK_PRS)

    captured = capsys.readouterr()

    assert captured.out == {}
