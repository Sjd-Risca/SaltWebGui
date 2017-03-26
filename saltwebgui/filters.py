# -*- coding: utf-8 -*-
"""Custom filter for jinja templateing"""
import re
from datetime import datetime
from jinja2 import Markup, escape


# https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
def pretty_date(value, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    NB: when/if Babel 1.0 releaseduse format_timedelta/timedeltaformat instead
    """
    now = datetime.utcnow()
    diff = now - value

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default


_PARAGRAPH_RE = re.compile(r'(?:\r\n|\r|\n){2,}')

def nl2br(value):
    """Html helper that will replace:

    - new line with <br>
    - double new line with <p></p>
    """
    if not value:
        return ""
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                          for p in _PARAGRAPH_RE.split(escape(value.strip())))
    return Markup(result)
