#!/usr/bin/env python3


'''
Sample Canonical Pegasus workflow in shape of a diamond to highlight
concepts.
'''

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

from Pegasus.api import *

logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# need to know where Pegasus is installed for notifications
PEGASUS_HOME = shutil.which('pegasus-version')
PEGASUS_HOME = os.path.dirname(os.path.dirname(PEGASUS_HOME))
PEGASUS_KEG_LOCATION = PEGASUS_HOME + "/bin/pegasus-keg"

# --- Work Dir Setup -----------------------------------------------------------

TOP_DIR = Path.cwd()
WORK_DIR = TOP_DIR / "work"

try:
    Path.mkdir(WORK_DIR)
except FileExistsError:
    pass


# --- Configuration ------------------------------------------------------------

print("Generating pegasus.conf at: {}".format(TOP_DIR / "pegasus.properties"))

props = Properties()
props["pegasus.data.configuration"] = "condorio"
props["pegasus.monitord.encoding"] = "json"                                                                    
props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
# speeds up tutorial workflows - remove for production ones
props["pegasus.mode"] = "tutorial"

props.write()

# --- Sites --------------------------------------------------------------------
LOCAL = "local"
CONDOR_POOL = "condorpool"

shared_scratch_dir = str(WORK_DIR / "shared-scratch")
local_storage_dir = str(WORK_DIR / "outputs" )

print("Generating site catalog at: {}".format(TOP_DIR / "sites.yml"))

SiteCatalog().add_sites(
    Site(
        LOCAL, arch=Arch.X86_64, os_type=OS.LINUX, os_release="rhel", os_version="7"
    ).add_directories(
        Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
            FileServer("file://" + shared_scratch_dir, Operation.ALL)
        ),
        Directory(Directory.LOCAL_STORAGE, local_storage_dir).add_file_servers(
            FileServer("file://" + local_storage_dir, Operation.ALL)
        ),
    ),
    Site(CONDOR_POOL, arch=Arch.X86_64, os_type=OS.LINUX)
    .add_pegasus_profile(style="condor")
    .add_pegasus_profile(auxillary_local="true")
    .add_condor_profile(universe="vanilla"),
).write()

# --- Replicas -----------------------------------------------------------------

print("Generating replica catalog at: {}".format(TOP_DIR / "replicas.yml"))

# create initial input file
with open("f.a", "w") as f:
    f.write("This is sample input to KEG\n")

fa = File("f.a").add_metadata({"creator": "vahi"})
ReplicaCatalog().add_replica(LOCAL, fa, TOP_DIR / fa.lfn).write()

# --- Transformations ----------------------------------------------------------

print(
    "Generating transformation catalog at: {}".format(TOP_DIR / "transformations.yml")
)

preprocess = Transformation("preprocess", namespace="pegasus", version="5.0").add_sites(
    TransformationSite(
        LOCAL,
        PEGASUS_KEG_LOCATION,
        is_stageable=True,
        arch=Arch.X86_64,
        os_type=OS.LINUX,
    )
)

findrage = Transformation("findrange", namespace="pegasus", version="5.0").add_sites(
    TransformationSite(
        LOCAL,
        PEGASUS_KEG_LOCATION,
        is_stageable=True,
        arch=Arch.X86_64,
        os_type=OS.LINUX,
    )
)

analyze = Transformation("analyze", namespace="pegasus", version="5.0").add_sites(
    TransformationSite(
        CONDOR_POOL,
        PEGASUS_KEG_LOCATION,
        is_stageable=True,
        arch=Arch.X86_64,
        os_type=OS.LINUX,
    )
)

TransformationCatalog().add_transformations(preprocess, findrage, analyze)\
        .write("transformations.yml")

# --- Workflow -----------------------------------------------------------------
print("Generating workflow")

fb1 = File("f.b1")
fb2 = File("f.b2")
fc1 = File("f.c1")
fc2 = File("f.c2")
fd = File("f.d")

try:
    Workflow("blackdiamond").add_jobs(
        Job(preprocess)
        .add_args("-a", "preprocess", "-T", "60", "-i", fa, "-o", fb1, fb2)
        .add_inputs(fa)
        .add_outputs(fb1, fb2, register_replica=True),
        Job(findrage)
        .add_args("-a", "findrange", "-T", "60", "-i", fb1, "-o", fc1)
        .add_inputs(fb1)
        .add_outputs(fc1, register_replica=True),
        Job(findrage)
        .add_args("-a", "findrange", "-T", "60", "-i", fb2, "-o", fc2)
        .add_inputs(fb2)
        .add_outputs(fc2, register_replica=True),
        Job(analyze)
        .add_args("-a", "analyze", "-T", "60", "-i", fc1, fc2, "-o", fd)
        .add_inputs(fc1, fc2)
        .add_outputs(fd, register_replica=True),
    ).plan(
        dir=str(WORK_DIR),
        verbose=3,
        sites=[CONDOR_POOL],
        output_sites=[LOCAL],
        force=True,
        submit=True,
    )
except PegasusClientError as e:
    print(e.output)
    
