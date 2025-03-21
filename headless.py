import bpy
import argparse
import sys


class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1 :]  # the list after '--'
        except ValueError as e:  # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())


parser = ArgumentParserForBlender(description="Run pigeons in headless mode")
parser.add_argument(
    "--hw",
    type=str,
    help="The homework to run",
    required=True,
)
parser.add_argument(
    "--homework-file",
    type=str,
    help="The file containing the homework",
    required=True,
)
parser.add_argument(
    "--output-to-console",
    action="store_true",
    help="Output results to console",
)

parser.add_argument(
    "--output-to-file",
    type=str,
    default="",
    help="Output results to a file",
)


args = parser.parse_args()


if __name__ == "__main__":
    if not args.homework_file.endswith(".blend"):
        raise ValueError("The homework file must be a .blend file")
    if bpy.ops.pigeons.test_runner_operator is None:
        raise ValueError(
            "The test runner operator is not registered, make sure the addon is enabled"
        )

    bpy.ops.wm.open_mainfile(filepath=args.homework_file)
    bpy.ops.pigeons.test_runner_operator(
        current_hw=args.hw,
        output_to_console=args.output_to_console,
        output_to_file=args.output_to_file,
    )
