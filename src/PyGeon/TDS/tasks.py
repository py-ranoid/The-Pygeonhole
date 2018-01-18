from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from TDS.overwatch import job, CPjob, Meetupjob, Hackjob


@task(name="nightswatch")
def jobinit():
    Meetupjob()
    Hackjob()


@task(name="noobswatch")
def jobinit():
    print "Exec"


@task(name="surdswatch")
def jobinit():
    CPjob()
