import sys

import diskcache

cache = diskcache.Cache("cache", size_limit=sys.maxsize)
