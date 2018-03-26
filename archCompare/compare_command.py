from archCompare.compareArchive import ArchCompare
import sys
import os
import argparse
import pkg_resources

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
version = pkg_resources.require("archCompare")[0].version


def main():
    usage = "\n %prog [options] -a archive_a.tar -b archive_b.tar -j fileTypes.json -c name"

    optParser = argparse.ArgumentParser(prog='cgpCompare')
    optional = optParser._action_groups.pop()
    required = optParser.add_argument_group('required arguments')

    required.add_argument("-a", "--archive_a", type=str, dest="archive_a", required=True,
                          default="", help="archive path for a folder, file or a tar data")

    required.add_argument("-b", "--archive_b", type=str, dest="archive_b", required=True,
                          default="", help="archive path for a folder, file or a tar data")

    required.add_argument("-j", "--json_config", type=str, dest="json_config", required=True,
                          default=None, help="path to json config file")

    optional.add_argument("-o", "--outfile", type=str, dest="outfile",
                          default=None, help="path to outfile file, STOUT if not provided")

    optional.add_argument("-c", "--cmp_type", type=str, nargs='*', dest="cmp_type", required=False,
                          default=None, help="Compariosn type to perform [ \
                           compares archives using space separated list of paramaters, \
                           name: perform comparsion based on file name \
                           size: perform comparsion based on file size \
                           checksum: perform comparsion based on checksum tool defined in json config file \
                           diffs: does full data comparison based on tools defined for each extension type in\
                           json file's diffs section \
                           Note- command line option if set overrides default reportsOn \
                           values in json config file ]")

    optional.add_argument("-r", "--remove_tmp", type=str, dest="remove_tmp", required=False,
                          default='y', help="remove tmporary data, default is 'y'")

    optional.add_argument("-v", "--version", action='version', version='%(prog)s ' + version)
    optional.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True)

    optParser._action_groups.append(optional)

    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit(1)
    opts = optParser.parse_args()
    if not (opts.archive_a or opts.archive_b):
        sys.exit('\nERROR Arguments required\n\tPlease run: cgpCompare --help\n')
    # vars function returns __dict__ of Namespace instance
    mycomp = ArchCompare(**vars(opts))
    mycomp.run_comparison()
