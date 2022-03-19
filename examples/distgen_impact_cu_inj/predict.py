from slac_services.services.scheduling import MountPoint
from slac_services.utils import isotime
from slac_services import service_container
import argparse
import numpy as np
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


LUME_CONFIGURATION_FILE = os.environ["LUME_ORCHESTRATION_CLUSTER_CONFIG"]


distgen_input_filename = f"{dir_path}/files/distgen.yaml"

# we need to create mount points for each of these
# use the scheduling MountPoint utility
distgen_input_mount = MountPoint(
    name="distgen-input-mount", host_path=distgen_input_filename, mount_type="File"
)


# format inputs
vcc_array = np.load(f"{dir_path}/files/default_vcc_array.npy")

distgen_pv_values = {
    "CAMR:IN20:186:RESOLUTION" : 9,
    "CAMR:IN20:186:RESOLUTION.EGU" : "um",
    "CAMR:IN20:186:N_OF_ROW" : 480,
    "CAMR:IN20:186:N_OF_COL": 640,
    "CAMR:IN20:186:IMAGE": vcc_array.tolist(), # neet to convert to json serializable input for passed data
    "BPMS:IN20:221:TMIT": 1.51614e+09
}

distgen_configuration = {}
distgen_settings = {
    'n_particle': 10000,
    "t_dist:length:value":  4 * 1.65   #  Inferred pulse stacker FWHM: 4 ps, converted to tukey length
}

distgen_pvname_to_input_map = {
    "CAMR:IN20:186:RESOLUTION" : "vcc_resolution",
    "CAMR:IN20:186:RESOLUTION.EGU" : "vcc_resolution_units",
    "CAMR:IN20:186:N_OF_ROW" : "vcc_size_y",
    "CAMR:IN20:186:N_OF_COL": "vcc_size_x",
    "CAMR:IN20:186:IMAGE": "vcc_array",
    "BPMS:IN20:221:TMIT":"total_charge"
}


workdir = f"{dir_path}/files/output"
# will want to create a directory so use DirectoryOrCreate mount type
workdir_mount = MountPoint(
    name="workdir-mount", host_path=workdir, mount_type="DirectoryOrCreate"
)


# in this case, will be using conda installation of impact
command="ImpactTexe"
command_mpi=""
use_mpi=False
mpi_run="mpirun -n {nproc} --use-hwthread-cpus {command_mpi}"

impact_configuration = {
    "command": command,
    "command_mpi": command_mpi,
    "use_mpi": use_mpi,
    "workdir": workdir,
    "mpi_run": mpi_run
}

impact_settings = {
    "header:Nx": 32,
    "header:Ny": 32,
    "header:Nz": 32,
    "stop": 16.5,
  #  "stop": 8,
    "numprocs": 1,
    "timeout": 1000,
    "total_charge": 0, # for debugging
}

impact_archive_file = f"{dir_path}/files/archive.h5"
impact_archive_input_mount = MountPoint(
    name="impact-archive-input-mount", host_path=impact_archive_file, mount_type="File"
)

impact_pv_values = {"SOLN:IN20:121:BACT": 0.47235,
                        "QUAD:IN20:121:BACT":  -0.00133705,
                        "QUAD:IN20:122:BACT": 0.000769202,
                        "ACCL:IN20:300:L0A_PDES": 0,
                        "ACCL:IN20:400:L0B_PDES": -2.5,
                        "ACCL:IN20:300:L0A_ADES": 58,
                        "ACCL:IN20:400:L0B_ADES": 69.9586,
                        "QUAD:IN20:361:BACT": -3.25386,
                        "QUAD:IN20:371:BACT": 2.5843,
                        "QUAD:IN20:425:BACT": -1.54514,
                        "QUAD:IN20:441:BACT": -0.671809,
                        "QUAD:IN20:511:BACT": 3.22537,
                        "QUAD:IN20:525:BACT": -3.20496,
                        }

impact_pvname_to_input_map = {"SOLN:IN20:121:BACT": "SOL1:solenoid_field_scale",
                "QUAD:IN20:121:BACT": "CQ01:b1_gradient",
                "QUAD:IN20:122:BACT": "SQ01:b1_gradient",
                "ACCL:IN20:300:L0A_PDES": "L0A_phase:dtheta0_deg",
                "ACCL:IN20:400:L0B_PDES": "L0B_phase:dtheta0_deg",
                "ACCL:IN20:300:L0A_ADES": "L0A_scale:voltage",
                "ACCL:IN20:400:L0B_ADES": "L0B_scale:voltage",
                "QUAD:IN20:361:BACT": "QA01:b1_gradient",
                "QUAD:IN20:371:BACT": "QA02:b1_gradient",
                "QUAD:IN20:425:BACT": "QE01:b1_gradient",
                "QUAD:IN20:441:BACT": "QE02:b1_gradient",
                "QUAD:IN20:511:BACT": "QE03:b1_gradient",
                "QUAD:IN20:525:BACT": "QE04:b1_gradient",
                }


# DirectoryOrCreate for archive and dashboard
archive_dir = f"{dir_path}/files/output/archive"
impact_archive_mount = MountPoint(
    name="archive-mount", host_path=archive_dir, mount_type="DirectoryOrCreate"
)

dashboard_dir = f"{dir_path}/files/output/dashboard"
dashboard_mount = MountPoint(
    name="dashboard-mount", host_path=dashboard_dir, mount_type="DirectoryOrCreate"
)


data = {
    "distgen_input_filename": distgen_input_filename,
    "distgen_settings": distgen_settings,
    "distgen_configuration": distgen_configuration,
    "distgen_pv_values": distgen_pv_values,
    "distgen_pvname_to_input_map": distgen_pvname_to_input_map,
    "impact_configuration": impact_configuration,
    "impact_pv_values": impact_pv_values,
    "impact_settings": impact_settings,
    "impact_pvname_to_input_map": impact_pvname_to_input_map,
    "impact_archive_file": impact_archive_file,
    "pv_collection_isotime": isotime(),
    "impact_archive_dir": archive_dir,
    "dashboard_dir": dashboard_dir
}


# get remote modeling service
remote_modeling_service = service_container.remote_modeling_service()
mount_points = [distgen_input_mount, workdir_mount, impact_archive_input_mount, impact_archive_mount, dashboard_mount]
remote_modeling_service.predict(model_id=1, data=data, mount_points=mount_points, lume_configuration_file=LUME_CONFIGURATION_FILE)
#from distgen_impact_cu_inj_ex.flow.flow import get_flow
#flow = get_flow()

#flow.run(**data)
    
    