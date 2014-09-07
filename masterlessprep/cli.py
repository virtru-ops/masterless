"""
Command line interface to salt-masterless-prep

This should be useful for testing
"""
import sys
import argparse
import logging
from pythonjsonlogger import jsonlogger
from .processor import MasterlessTemplate

DESCRIPTION = 'Prepares a masterless template to be used as a salt masterless folder structure'

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('masterless_file', help='The masterless.yml file')
#parser.add_argument('-d, --destination', help='The destination')


def run(args=None):
    args = args or sys.argv[1:]

    # Parse the arguments
    parsed_args = parser.parse_args(args)

    # Load the masterless template
    template = MasterlessTemplate.from_yaml(parsed_args.masterless_file)
    template.build()
