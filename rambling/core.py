from __future__ import absolute_import, division, print_function

import os
import subprocess
import requests
import logging
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

JAR_FILE = "rambling-1.0-SNAPSHOT.jar"
JAVA_APP = "com.continuumio.rambling.Client"


class Rambling(object):
    def __init__(self, namenode="localhost", nm_port=9000, resourcemanager="localhost", rm_port=9026):
        """
        Connection to HDFS/YARN
        Parameters
        ----------
        namenode: str
            Namenode hostname/ip
        nm_port: int
            Namenode Port (default: 9000)
        resourcemanager: str
            Resource Manager hostname/ip
        rm_port: int
            Resource Manager port (default: 9026)
        """
        self.namenode = os.environ.get("NAMENODE") or namenode
        self.nm_port = nm_port

        self.resourcemanager = os.environ.get("RESOURCEMANAGER") or resourcemanager
        self.rm_port = rm_port

    @property
    def HDFS_JAR_PATH(self):
        host_port = "{}:{}".format(self.namenode, self.nm_port)
        return os.path.join("hdfs://", host_port, "jars", JAR_FILE)



    def start_application(self, cmd, num_containers=1):
        """
        Method to start a yarn app with a distributed shell

        Parameters
        ----------
        num_containers: int
            number of containers to start (default 1)

        cmd: str
            command to run in each yarn container

        Returns
        -------
        applicationId: str
            A yarn application ID string

        """

        JAR_FILE_PATH = os.path.join(os.path.dirname(__file__), "java_libs", JAR_FILE)
        args = ["hadoop", "jar", JAR_FILE_PATH, JAVA_APP, self.HDFS_JAR_PATH, str(num_containers), cmd]

        proc = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        logger.debug(out)
        logger.debug(err)
        # last string in out is applicationId
        # TODO Better JAVA Python communcation: appId, Resources, Yarn, etc.
        appId = out.split()[-1]
        return appId



    def get_application_logs(self, app_id):
        """

        Parameters
        ----------
        app_id: str
             A yarn application ID string

        Returns
        -------
        log: dictionary
            logs from each container
        """
        host_port = "{}:{}".format(self.resourcemanager, self.rm_port)
        url = "http://{}/ws/v1/cluster/apps/{}".format(host_port, app_id)
        logger.debug("Getting Resource Manager Info: {}".format(url))
        r = requests.get(url)
        data = r.json()
        logger.debug(data)

        try:
            amHostHttpAddress = data['app']['amHostHttpAddress']
        except KeyError:
            msg = "Local logs unavailable. State: {} finalStatus: {} Possibly check logs " \
                  "with `yarn logs -applicationId`".format(data['app']['state'], data['app']['finalStatus'])
            raise Exception(msg)

        url = "http://{}/ws/v1/node/containers".format(amHostHttpAddress)
        r = requests.get(url)
        data = r.json()['containers']['container']
        logger.debug(data)

        #container_1452274436693_0001_01_000001
        get_app_id_num = lambda x: "_".join(x.split("_")[1:3])

        app_id_num = get_app_id_num(app_id)
        containers = [d for d in data if get_app_id_num(d['id']) == app_id_num]

        logs = {}
        for c in containers:
            log = {}
            log['nodeId'] = c['nodeId']

            # grab stdout
            url = "{}/stdout/?start=0".format(c['containerLogsLink'])
            logger.debug("Gather stdout/stderr data from {}: {}".format(c['nodeId'], url))
            r = requests.get(url)
            log['stdout'] = r.text

            # grab stderr
            url = "{}/stderr/?start=0".format(c['containerLogsLink'])
            r = requests.get(url)
            log['stderr'] = r.text

            logs[c['id']] = log

        return logs