"""
A TiddlyWeb plugin which adds a _hash field to a tiddler when it is
retrieved from the store:

* When a tiddler is get from the store, if there is no _hash, then the
  hash is added to the outgoing tiddler. It is _not_ saved

This is done to allow quick comparisons between tiddlers which may have
different names but may have the same set of content characteristics.

By default the attribute from which the digest is created is 'text'.

The hash_tiddler method is exposed so that stores can create a hash
prior to a put to the store. See tiddlywebplugis.tiddlyspace.store for
an example.

Copyright 2010-2011, Chris Dent <cdent@peermore.com>
Licensed under the same terms as TiddlyWeb: BSD License

To use add 'tiddlywebplugins.hashmaker' to system_plugins and
twanager_plugins in tiddlywebconfig.py. Optionally define
hashmaker.attributes to be a list of strings representing the attributes
or fields of a tiddler which are to be hashed. The default is:

    ['text']
"""
__version__ = '0.6'

import logging

from tiddlyweb.store import HOOKS
from tiddlyweb.util import sha


def hash_tiddler_hook(storage, tiddler):
    """
    Wrap hash_tiddler in the hook signature.
    """
    hash_tiddler(storage.environ, tiddler)


def hash_tiddler(environ, tiddler, overwrite=False):
    """
    Given tiddler, add a _hash field which is a digest of the
    attributes named in config['hashmaker.attributes'].
    """
    if overwrite or '_hash' not in tiddler.fields:
        config = environ['tiddlyweb.config']
        attributes = config.get('hashmaker.attributes', ['text'])
        digest = sha()
        for attribute in attributes:
            try:
                data = getattr(tiddler, attribute)
            except AttributeError:
                data = tiddler.fields.get(attribute, '')
            try:
                try:
                    digest.update(data.encode('utf-8'))
                except (UnicodeEncodeError, UnicodeDecodeError):
                    digest.update(data)
            except (AttributeError, TypeError), exc:
                logging.warn('tiddler data invalid for hashing: %s:%s, %s:%s',
                        tiddler.bag, tiddler.title, attribute, data)
        tiddler.fields[u'_hash'] = unicode(digest.hexdigest())


def init(config):
    """
    Establish the hook and validator.
    """
    HOOKS['tiddler']['get'].append(hash_tiddler_hook)
