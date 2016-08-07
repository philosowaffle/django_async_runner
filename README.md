# django_async_runner
A very simple barebones async runner for django

Modified from: http://stancarney.co/2013/01/simple-django-asynchronous-processing/

This async_runner works by creating Task objects that are added to a queue.  Each of these Task objects contains a python script to be executed.  A async_runner loops over the Tasks table repeatedly looking for Tasks to execute.  It will attempt to execute a given Task a set number of times before giving up.  When the async_runner runs out of Tasks to execute it will cancel itself.  The async_runner also looks for a stop task in the table and will cancel its run when it sees it.  This async runner is simple enough that any of the aforementioned behaviour can be easily modified to meet your needs.

Add the objects found in `models.py` to your applications existing `models.py`.  Copy paste the `async_runner.py` file at the same level as your applications `models.py`.

## Example Usage

### Simple Example
This example simple iterates over an array of items and creates a Task for each that prints the item to the screen.

```python
from .models import Task, Async

import async_runner as async_runner

import thread

items = ["some", "stuff"]

for item in items:
  task = Task()
  task.script = "print \"" + item + "\""
  task.save()
  
thread.start_new_thread(async_runner.start())
```

### More Complex Example
This example creates a set of sql queries to be executed.  Note: this is not necessarily the most efficient way to write this since it creates and closes the sql connection for each UPDATE, but it demonstrates the basic mechanics of how to use async_runner to run DB queries on a separate thread.

```python
from .models import Task, Async

import async_runner as async_runner

import thread

script = """
conn = sqlite3.connect(\'{}\')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

query = {}

try:
    cursor.executescript(query)
    conn.commit()
except Exception as e:
    if cursor:
        conn.rollback()
        cursor.close()
        self.log_error("Failed to run query against the database: " + query, e)
    raise e

if cursor:
    cursor.close()
"""


dummy_data = DummyObject.objects.all()
for data in dummy_data:
  q = "UPDATE SomeTable SET play_count = {} WHERE id = {};".format(data.play_count, data.id)
  task = Task()
  task.script = script.format(q)
  task.save()

thread.start_new_thread(async_runner.start())
```


