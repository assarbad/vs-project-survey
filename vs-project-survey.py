#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set autoindent smartindent softtabstop=4 tabstop=4 shiftwidth=4 expandtab:
from __future__ import print_function, with_statement, unicode_literals, division, absolute_import

__author__ = "Oliver Schneider"
__copyright__ = "2023 Oliver Schneider (assarbad.net), under the terms of the UNLICENSE"
__version__ = "0.1.0"
__compatible__ = (
    (3, 7),
    (3, 8),
    (3, 9),
    (3, 10),
    (3, 11),
)
__doc__ = """
=========
 PROGRAM
=========
"""
import argparse  # noqa: F401
import os  # noqa: F401
import sys
import fnmatch
import re
import xml.etree.ElementTree as ET

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

# Checking for compatibility with Python version
if not sys.version_info[:2] in __compatible__:
    sys.exit(
        "This script is only compatible with the following Python versions: %s."
        % (", ".join(["%d.%d" % (z[0], z[1]) for z in __compatible__]))
    )  # pragma: no cover


def parse_args():
    """ """
    from argparse import ArgumentParser

    parser = ArgumentParser(description="This helps to survey existing MSBuild-based C++ projects")
    parser.add_argument(
        "dirs", metavar="DIRECTORY", type=str, nargs="+", help="Directories in which to apply the changes"
    )
    return parser.parse_args()


class VcxProj(object):
    XMLNS = "{http://schemas.microsoft.com/developer/msbuild/2003}"
    EXPECTED_CONFIGS = {
        "Release|Win32",
        "Release|x64",
        "Debug|Win32",
        "Debug|x64",
    }
    __fpath, __root, __tree = None, None, None

    def __init__(self, fpath):
        self.__fpath = fpath
        self.__tree = ET.parse(fpath)
        self.__root = self.__tree.getroot()
        # TODO: locate companion .filters file
        self.parse()

    @staticmethod
    @cache
    def stripns(tag):
        if tag.startswith(VcxProj.XMLNS):
            return tag[len(VcxProj.XMLNS) :]
        return tag

    def parse(self):
        fpath, root = self.__fpath, self.__root
        print(fpath)
        idx = 0
        for child in root:
            assert child.tag.startswith(self.XMLNS), "Current tag not part of XML namespace?"
            tag, attrib = self.stripns(child.tag), child.attrib
            print(tag, attrib)
            if idx in {0}:
                assert tag in {"ItemGroup"}, f"Expected child ({idx=}) is ItemGroup (project configurations)"
                assert attrib["Label"] in {"ProjectConfigurations"}, "Expecting project configurations here"
                for cfg in child.findall("./ProjectConfiguration"):
                    print(cfg.tag, cfg.attrib)
                    assert self.stripns(cfg.tag) in {"ProjectConfiguration"}
                    assert cfg.attrib["Include"] in self.EXPECTED_CONFIGS
            elif idx in {1}:
                assert tag in {"PropertyGroup"}, f"Expected child ({idx=}) is PropertyGroup (globals)"
                assert attrib["Label"] in {"Globals"}, "Expecting global properties here"
                for prop in child.findall("."):
                    print(prop.tag, prop.attrib)
            idx += 1


def process_project(fpath):
    project = VcxProj(fpath)


def main(**kwargs):
    """ """
    dirs = kwargs.get("dirs", ["."])
    for dir in dirs:
        if not os.path.exists(dir):
            print(f"Warning: {dir} not found.", file=sys.stderr)
        for r, _, fnames in os.walk(dir):
            for fn in fnmatch.filter(fnames, "*.vcxproj"):
                fpath = os.path.join(r, fn)
                process_project(fpath)
    return 0


if __name__ == "__main__":
    args = parse_args()
    try:
        sys.exit(main(**vars(args)))
    except SystemExit:
        pass
    except ImportError:
        raise  # re-raise
    except RuntimeError:
        raise  # re-raise
    except Exception:
        print(__doc__)
        raise  # re-raise
