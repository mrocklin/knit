Quickstart
----------

Install
~~~~~~~

Use ``pip`` or ``conda`` to install::

   $ pip install knit --upgrade
   $ conda install knit

Start Command
~~~~~~~~~~~~~

Instantiate ``knit`` with valid ResourceManager/Namenode IP/Ports and create a command string to run in
all YARN containers

.. code-block:: python

   >>> from knit import Knit
   >>> k = Knit(autodetect=True) # autodetect IP/Ports for YARN/HADOOP
   >>> cmd = 'date'
   >>> app_id = k.start(cmd)

``start`` also take parameters: ``num_containers``, ``memory``, and ``virtual_cores``

Status
~~~~~~

After starting/submitting a command you can monitor it's progress.  The ``status`` method communicates with YARN's
`ResourceManager`_ and returns a python dictionary with current monitoring data

.. code-block:: python

   >>> k.status(app_id)
   {'app': {'allocatedMB': 512,
  'allocatedVCores': 1,
  'amContainerLogs': 'http://192.168.1.3:8042/node/containerlogs/container_1454100653858_0011_01_000001/ubuntu',
  'amHostHttpAddress': '192.168.1.3:8042',
  'applicationTags': '',
  'applicationType': 'YARN',
  'clusterId': 1454100653858,
  'diagnostics': '',
  'elapsedTime': 123800,
  'finalStatus': 'UNDEFINED',
  'finishedTime': 0,
  'id': 'application_1454100653858_0011',
  'memorySeconds': 63247,
  'name': 'knit',
  'numAMContainerPreempted': 0,
  'numNonAMContainerPreempted': 0,
  'preemptedResourceMB': 0,
  'preemptedResourceVCores': 0,
  'progress': 0.0,
  'queue': 'default',
  'runningContainers': 1,
  'startedTime': 1454276990907,
  'state': 'ACCEPTED',
  'trackingUI': 'UNASSIGNED',
  'user': 'ubuntu',
  'vcoreSeconds': 123}}

Often a user will want to track the ``state`` of an application.  Possible ``states`` include: ``NEW``,
``NEW_SAVING``, ``SUBMITTED``, ``ACCEPTED``, ``RUNNING``, ``FINISHED``, ``FAILED``, ``KILLED``

Logs
~~~~

Users can retrieve log data directly from a ``RUNNING` Application Master::


   >>> k.logs(app_id)

Or if log aggregation is enabled, users can retrieve the resulting aggregated log data stored in HDFS.  Note:
aggregated log data is only available **after** the application has finished or been terminated::

   >>> k.logs(app_id, shell=True)


Kill
~~~~

When you need to stop an application from executing immediately, users can use the ``kill`` method:

::

   >>> k.kill(app_id)


Python Applications
~~~~~~~~~~~~~~~~~~~

A simple Python based application

.. code-block:: python

   from knit import Knit
   k = Knit()

   cmd = 'python -c "import sys; print(sys.version_info); import random; print(str(random.random()))"'
   app_id = k.start(cmd, num_containers=2)

A long running Python application

.. code-block:: python

   from knit import Knit
   k = Knit()

   cmd = 'python -m SimpleHTTPServer'
   app_id = k.start(cmd, num_containers=2)

.. _ResourceManager: https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/ResourceManagerRest.html
