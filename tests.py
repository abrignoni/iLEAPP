"""
What
====
This test suite runs as a "black box" testing mechanism.

Goal
====
The goal of this test suite is to test whether changes that a contributor is
making to the project on a local git branch will not change the behavior of the
project from whatever is on their local master branch.

Therefore, the tests assume that the local master branch on the user's system
is the "golden standard", i.e., master is stable.

Drawbacks
=========
This is not an ideal assumption, however it has been deemed a worthy compromise
in order to have _some_ tests to begin with, especially while making large
changes of the refactor variety, etc.

Usage
=====
The tests here rely on the user having test images in a folder called
./test_images.

This directory can be created on *nix systems with:
    mkdir -p test_images/

The phone test images will have to be supplied by the contributor at this time.

Future
======

The future of the test suite will include proper unit and integration tests. To
get to that point a lot of refactors are being made which will be much easier to
make with a test suite like this in place and prevent merging broken code to
master (which has been done before).
"""
import os
import subprocess
import unittest

import filetype
from bs4 import BeautifulSoup

from extraction import UnsupportedFileType, get_filetype


TEST_IMAGE_DIR = "./test_images"


def get_branch_to_test() -> str:
    """
    Returns currently checked out branch as a string.

    Assumes your current branch is the branch to test.
    """
    branch_to_test_cmd = "git rev-parse --abbrev-ref HEAD"
    return (
        subprocess.run(branch_to_test_cmd.split(" "), stdout=subprocess.PIPE)
        .stdout.strip()
        .decode()
    )


def checkout_branch(branch_name="master"):
    checkout_command = f"git checkout {branch_name}"
    print(f"Executing: {checkout_command}")
    return subprocess.run(checkout_command.split(" "))


def get_ileapp_output(filepath):
    """
    Runs the CLI version of ileapp and returns the output that one would have
    received on stdout.

    Returns None if the filetype is not supported.
    """
    try:
        ftype = get_filetype(filepath)
    except UnsupportedFileType:
        return

    cmd = f"python ileapp.py {filepath}"
    print(f"Executing: {cmd}")

    return subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)


reports = dict()


def collect_reports(branch_to_test):
    if branch_to_test == "master":
        print("Currently on master branch, nothing to do")
        return

    print("Collecting reports from different images, this may take a few minutes.")

    checkout_branch()

    for fname in os.listdir(TEST_IMAGE_DIR):
        fpath = os.path.join(TEST_IMAGE_DIR, fname)
        reports[fpath] = dict()
        output = get_ileapp_output(fpath)
        if output is None:
            continue
        reports[fpath]["master"] = output.stdout.strip().decode().split(" ")[-1]

    checkout_branch(branch_to_test)

    for fpath in reports.keys():
        output = get_ileapp_output(fpath)
        reports[fpath][branch_to_test] = output.stdout.strip().decode().split(" ")[-1]

    return reports


class TestReportSame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        branch_to_test = get_branch_to_test()
        cls.reports = collect_reports(branch_to_test)
        print(reports)

    def test_unique_id_consistent(self):
        """
        Tests that the unique device id is present in each report
        and is consistent for each image.
        """
        for test_image, branch_reports in self.reports.items():
            search_items = list()
            for branch in branch_reports.keys():
                fpath = os.path.join(branch_reports[branch], "_elements", "data.html")
                with open(fpath) as fp:
                    soup = BeautifulSoup(fp, "html.parser")
                search_items.append(soup.find(text="Unique Device ID").next.contents[0])
            self.assertEqual(search_items[0], search_items[1])


if __name__ == "__main__":
    unittest.main()
