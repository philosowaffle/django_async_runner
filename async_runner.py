import logging

# You will need to add imports for any dependencies your Task scripts have.  For instance, if your Tasks make updates to a
# sqlite DB then you should import sqlite3 here.
# import sqlite3

from time import sleep

from django.db import transaction
from .models import Task, Async

logger = logging.getLogger(__name__)

# How many times we will try to execute a Task before giving up
EXCEPTION_THRESHOLD = 3

# Starts a new async_runner
def start():

    # There is already an async task running, we do not need to create another one.
    # Change this logic if you allow more than one async runner at a time.
    if Async.objects.count() > 0:
        logger.info("Async runner already running, exiting.")
        return

    logger.info("Starting run...")

    # Create an entry to indicate an async runner exists
    # To support multiple async_runners you should modify the Async class to
    # have additional informative fields such as 'Name', 'Date Created', ect.
    async_object = Async()
    async_object.save()

    exception_count = 0
    stop = False
    current_task_id = None
    try:

        while not stop:
            try:
                with transaction.atomic():
                    tasks = Task.objects.filter(executed = False).order_by('id')
                    if len(tasks):
                        task = tasks[0]
                        current_task_id = task.id
                        if task.script == 'ASYNC_STOP':
                            stop = True
                        else:
                            exec(task.script)
                            exception_count = 0
                        # You can use these two lines instead if you wish to keep track of successfully completed
                        # Tasks.  Currently a Task is deleted from the DB upon success. 
                        # task.executed = True
                        # task.save()
                        # Delete on success
                        Task.objects.filter(id=task.id).delete()
                    else:
                        # Currently stopping the async_runner if no Tasks remain. Edit this to change
                        # this behavior.
                        current_task_id = None
                        Async.objects.first().delete()
                        stop = True
            except:
                logger.exception('Async Crashed')
                exception_count += 1

                # we need to mark the failed task as executed in another DB transaction.
                if current_task_id:
                    with transaction.atomic():
                        tasks = Task.objects.filter(id = current_task_id, executed = False).order_by(id)
                        if len(tasks):
                            task = tasks[0]
                            task.executed = True
                            task.save()

            if exception_count >= EXCEPTION_THRESHOLD:
                sleep(10)
            else:
                sleep(0.5)

    except Exception as e:
        logger.error("Async Runner exited early: " + str(e))
        Async.objects.first().delete()

# Adds a stop Task to the database, when any Async Runner encounters this task it will stop running and delete the Task.
def stop():
    Task.objects.create(script='ASYNC_STOP')
