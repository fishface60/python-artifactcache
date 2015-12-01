#!/usr/bin/python

from argparse import ArgumentParser

from xdg.BaseDirectory import save_cache_path

from . import __version__


parser = ArgumentParser(description=__doc__, prog=__package__)
parser.add_argument('--version', action='version',
                    version=('%(prog)s ' + __version__))
parser.add_argument('--base-directory', type=str,
                    default=save_cache_path('artifactcache'))
subparsers = parser.add_subparsers()

# commands: compose, save, list, delete
def compose():
	pass
# acache compose -a foo -a bar -E COMPOSE \
# -x acache save -a baz '*' -E SAVE \
# -x sh -c \
#    'git-cache clone-temporary --describeable "$REPO" --checkout "$SHA1" --ref "$ANCHOR_REF" "$COMPOSE/baz.build" "$@" ' - \
# -x git-chroot-safe --binds-env BIND --protects-env PROTECT \
# -x sh -c \
#    '# Note: This command is generated, filling in the chroot, commands and env vars where possible
#     # BIND and PROTECT are newline delimited, shell argv style word lists
#     set --
#     while read -r; do
#         eval set -- "$REPLY"
#     done <<<"$BIND" #TODO: posix sh compat
#     sandboxlib-run --writable-path /tmp --writable-path /baz.build --writable-path /baz.inst \
#                    --chdir "$COMPOSE/baz.build" --chroot "$COMPOSE" \
#                    --mount-extra "$SAVE" /baz.inst '' bind --env DESTDIR=/baz.inst \
