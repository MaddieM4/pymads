README
===================

This is a fork of a fork of Thomas Pinckney's pymds project.

 * Pinckney: http://code.google.com/p/pymds/
 * thekad: https://github.com/thekad/pymds

Overview
===================

pymads is an authoritative DNS server which makes all name resolution
decisions using external modules. pymads itself cannot resolve
anything. Instead, it relies on plugins which convert names in
client queries into responses that pymads then sends.

pymads differs from pymds in that it's designed for asynchronous
service/resolution, and it does not limit itself to specific DNS
zones. This allows you to use it as an "internet-wide" server. These
requirements are important for the project's intended use: the DNS
side of DJDNS.

What's included
===================

This source distribution contains:

1) pymads -- The core DNS server itself.

2) pymadsfile -- A plugin for answering queries based on a text file
database. This is a "source" plugin in pymads parlance. See below for
the format of the database file syntax.

3) pymadsrr -- A plugin that randomizes the order of multiple A record
responses. This is a "filter" plugin as opposed to a "source"
plugin. Thus, it cannot resolve names to answers, only alter the
answers that some "source" plugin has already provided.

Usage
===================

pymads is tested on Python 2.6-3.3.

Unlike pymds, pymads is not intended to be used as a standalone
server. pymads is intended to work as a callback-based component of
a larger program, acting as a self-contained library, configured
programmatically rather than through config files.

Configuration
===================

See the examples/ directory for configuration file examples.

Source, reporting bugs, etc
===================

See [the issue tracker](https://github.com/campadrenalin/pymads/issues).
