from __future__ import unicode_literals

from django.db import models

from django.utils.encoding import python_2_unicode_compatible

import os

@python_2_unicode_compatible
class Async(models.Model):
# A simple object for keeping track of how many async_runners are currently running.  To keep track simply
# add and remove Async objects from the database.

    # FIELDS
    asyncExists = models.BooleanField(default=True)

    def __str__(self):
        return 'AsyncExists: {}'.format(asyncExists)
        
@python_2_unicode_compatible
class Task(models.Model):
# Tasks to be run by the async_runner

    # FIELDS
    script = models.TextField()
    executed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Script: {}' \
                '\nExecuted: {}' \
                '\nDate Created: {}' \
                '\nLast Modified: {}'.format(script, executed, date_created, last_modified)
