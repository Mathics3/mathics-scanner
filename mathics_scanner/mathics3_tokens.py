"""
Command-line routine to how scanner tokenizes text.
"""
import argparse
import locale
import os
import re
import sys

from mathics_scanner.feed import FileLineFeeder, LineFeeder, SingleLineFeeder
from mathics_scanner.tokeniser import Tokeniser
from mathics_scanner.version import __version__


class TerminalShell(LineFeeder):
    def __init__(
        self,
        colors,
        want_readline,
        in_prefix: str = "In",
        out_prefix: str = "Out",
    ):
        super(TerminalShell, self).__init__("<stdin>")
        self.input_encoding = locale.getpreferredencoding()
        self.lineno = 0
        self.in_prefix = in_prefix
        self.out_prefix = out_prefix

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        try:
            if want_readline:
                self.using_readline = sys.stdin.isatty() and sys.stdout.isatty()
                self.ansi_color_re = re.compile("\033\\[[0-9;]+m")
        except ImportError:
            pass

        # Try importing colorama to escape ansi sequences for cross platform
        # colors
        try:
            from colorama import init as colorama_init
        except ImportError:
            colors = "NoColor"
        else:
            colorama_init()
            if colors is None:
                terminal_supports_color = (
                    sys.stdout.isatty() and os.getenv("TERM") != "dumb"
                )
                colors = "Linux" if terminal_supports_color else "NoColor"

        color_schemes = {
            "NOCOLOR": (["", "", "", ""], ["", "", "", ""]),
            "NONE": (["", "", "", ""], ["", "", "", ""]),
            "LINUX": (
                ["\033[32m", "\033[1m", "\033[0m\033[32m", "\033[39m"],
                ["\033[31m", "\033[1m", "\033[0m\033[31m", "\033[39m"],
            ),
            "LIGHTBG": (
                ["\033[34m", "\033[1m", "\033[22m", "\033[39m"],
                ["\033[31m", "\033[1m", "\033[22m", "\033[39m"],
            ),
        }

        # Handle any case by using .upper()
        term_colors = color_schemes.get(colors.upper())
        if term_colors is None:
            out_msg = "The 'colors' argument must be {0} or None"
            print(out_msg.format(repr(list(color_schemes.keys()))))
            sys.exit()

        self.incolors, self.outcolors = term_colors

    def empty(self):
        return False

    def feed(self):
        result = self.read_line(self.get_in_prompt()) + "\n"
        if result == "\n":
            return ""  # end of input
        self.lineno += 1
        return result

    def get_last_line_number(self):
        return self.lineno

    def get_in_prompt(self):
        next_line_number = self.get_last_line_number() + 1
        self.lineno = next_line_number
        return "{1}{0}[{2}{3}]:= {4}".format(self.in_prefix, *self.incolors)

    def get_out_prompt(self, form=None):
        line_number = self.get_last_line_number()
        if form:
            return "{2}{0}[{3}{4}]//{1}= {5}".format(
                self.out_prefix, line_number, form, *self.outcolors
            )
        return "{1}{0}[{2}{3}]= {4}".format(
            self.out_prefix, line_number, *self.outcolors
        )

    def to_output(self, text, form=None):
        line_number = self.get_last_line_number()
        newline = "\n" + " " * len("Out[{0}]= ".format(line_number))
        if form:
            newline += (len(form) + 2) * " "
        return newline.join(text.splitlines())

    def out_callback(self, out, fmt=None):
        print(self.to_output(str(out), fmt))

    def read_line(self, prompt):
        if self.using_readline:
            return self.rl_read_line(prompt)
        return input(prompt)

    def reset_lineno(self):
        self.lineno = 0

    def rl_read_line(self, prompt):
        # Wrap ANSI colour sequences in \001 and \002, so readline
        # knows that they're nonprinting.
        prompt = self.ansi_color_re.sub(lambda m: "\001" + m.group(0) + "\002", prompt)

        return input(prompt)


def tokenizer_loop(feeder: FileLineFeeder, code_tokenize_format: bool):
    """
    A read eval/loop for things having file input `feeder`.
    """
    while not feeder.eof:
        tokeniser = Tokeniser(feeder)
        print(f"Line: {feeder.lineno}:")
        while True:
            token = tokeniser.next()
            if token.tag == "END":
                break
            elif code_tokenize_format:
                print("  ", token.code_tokenize_format)
            else:
                print("  ", token)


def interactive_eval_loop(shell: TerminalShell, code_tokenize_format: bool):
    """
    A read eval/loop for an interactive session.
    `shell` is a shell session
    """
    while True:
        try:
            tokens(shell.feed(), code_tokenize_format)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print("\n\nGoodbye!\n")
            break
        except SystemExit:
            print("\n\nGoodbye!\n")
            # raise to pass the error code on, e.g. Quit[1]
            raise
        finally:
            shell.reset_lineno()


def tokens(code, code_tokenize_format: bool):
    tokeniser = Tokeniser(SingleLineFeeder(code))
    while True:
        token = tokeniser.next()
        if token.tag == "END":
            break
        elif code_tokenize_format:
            print(token.code_tokenize_format)
        else:
            print(token)


def main():
    argparser = argparse.ArgumentParser(
        prog="mathics3-tokens",
        usage="%(prog)s [options] [FILE]",
        add_help=False,
        description="A simple command-line to show Mathics tokens",
    )

    argparser.add_argument(
        "FILE",
        nargs="?",
        type=argparse.FileType("r"),
        help="parse tokens from FILE",
    )

    argparser.add_argument(
        "--help", "-h", help="show this help message and exit", action="help"
    )

    argparser.add_argument(
        "--colors",
        nargs="?",
        help=(
            "interactive shell colors. Use value 'NoColor' or 'None' to disable "
            "ANSI color decoration"
        ),
    )

    argparser.add_argument(
        "--post-mortem",
        help="go to post-mortem debug on a terminating system exception (needs trepan3k)",
        action="store_true",
    )

    argparser.add_argument(
        "--CodeTokenize",
        "-C",
        help="show tokens more like the way CodeTokenize does",
        action="store_true",
    )

    argparser.add_argument(
        "--quiet", "-q", help="don't print message at startup", action="store_true"
    )

    argparser.add_argument(
        "--no-readline",
        help="disable line editing",
        action="store_true",
    )

    argparser.add_argument(
        "--version", "-v", action="version", version="%(prog)s " + __version__
    )

    args, _ = argparser.parse_known_args()

    shell = TerminalShell(
        args.colors,
        want_readline=not (args.no_readline),
    )

    if args.post_mortem:
        try:
            from trepan.post_mortem import post_mortem_excepthook
        except ImportError:
            print(
                "trepan3k is needed for post-mortem debugging --post-mortem option ignored."
            )
            print("And you may want also trepan3k-mathics3-plugin as well.")
        else:
            sys.excepthook = post_mortem_excepthook

    if args.FILE is not None:
        feeder = FileLineFeeder(args.FILE)
        tokenizer_loop(feeder, args.CodeTokenize)

    else:
        interactive_eval_loop(shell, args.CodeTokenize)


if __name__ == "__main__":
    sys.exit(main())
