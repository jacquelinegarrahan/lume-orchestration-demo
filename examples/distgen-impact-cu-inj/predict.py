from slac_services.services.scheduling import MountPoint
from slac_services import service_container
from impact.tools import isotime # probably should have own utility
import argparse
import numpy as np
import os

dir_path = os.path.dirname(os.path.realpath(__file__))



parser = argparse.ArgumentParser()
parser.add_argument('flow_id', help='flow_id')
args = parser.parse_args()

flow_id = parser.flow_id


LUME_CONFIGURATION_FILE = os.eviron["LUME_ORCHESTRATION_CLUSTER_CONFIG"]


distgen_input_filename = f"{dir_path}/files/distgen.yaml"
distgen_output_filename = f"{dir_path}/files/output_file.txt"

# we need to create mount points for each of these
# use the scheduling MountPoint utility
distgen_input_mount = MountPoint(
    name="distgen_input_mount", host_path=distgen_input_filename, mount_type="File"
)
distgen_output_mount = MountPoint(
    name="distgen_output_mount", host_path=distgen_output_filename, mount_type="File"
)



# format inputs
vcc_array = np.load(f"{dir_path}/files/default_vcc_array.npy")

distgen_pv_values = {
    "vcc_resolution" : 9,
    "vcc_resolution_units" : "um",
    "vcc_size_y" : 480,
    "vcc_size_x": 640,
    "vcc_array": vcc_array.tolist(), # neet to convert to json serializable input for passed data
    "BPMS:IN20:221:TMIT": 1.51614e+09
}

distgen_configuration = {}
distgen_settings = {
    'n_particle': 5000,
    "t_dist:length:value":  4 * 1.65   #  Inferred pulse stacker FWHM: 4 ps, converted to tukey length
}

distgen_pvname_to_input_map = {
    "vcc_resolution" : "vcc_resolution",
    "vcc_resolution_units" : "vcc_resolution_units",
    "vcc_size_y" : "vcc_size_y",
    "vcc_size_x": "vcc_size_x",
    "vcc_array": "vcc_array",
    "BPMS:IN20:221:TMIT":"total_charge"
}


workdir = f"{dir_path}/files/output"
# will want to create a directory so use DirectoryOrCreate mount type
workdir_mount = MountPoint(
    name="workdir_mount", host_path=workdir, mount_type="DirectoryOrCreate"
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
    "numprocs": 1,
    "timeout": 1000
}

impact_archive_file = f"{dir_path}/files/lcls_injector/archive.h5"
impact_archive_input_mount = MountPoint(
    name="impact_archive_input_mount", host_path=impact_archive_file, mount_type="File"
)

impact_pv_values = {"SOL1:solenoid_field_scale": 0.47235,
                        "CQ01:b1_gradient":  -0.00133705,
                        "SQ01:b1_gradient": 0.000769202,
                        "L0A_phase:dtheta0_deg": 0,
                        "L0B_phase:dtheta0_deg": -2.5,
                        "L0A_scale:voltage": 58,
                        "L0B_scale:voltage": 69.9586,
                        "QA01:b1_gradient": -3.25386,
                        "QA02:b1_gradient": 2.5843,
                        "QE01:b1_gradient": -1.54514,
                        "QE02:b1_gradient": -0.671809,
                        "QE03:b1_gradient": 3.22537,
                        "QE04:b1_gradient": -3.20496,
                        }

impact_pvname_to_input_map = {"SOL1:solenoid_field_scale": "SOL1:solenoid_field_scale",
                "CQ01:b1_gradient": "CQ01:b1_gradient",
                "SQ01:b1_gradient": "SQ01:b1_gradient",
                "L0A_phase:dtheta0_deg": "L0A_phase:dtheta0_deg",
                "L0B_phase:dtheta0_deg": "L0B_phase:dtheta0_deg",
                "L0A_scale:voltage": "L0A_scale:voltage",
                "L0B_scale:voltage": "L0B_scale:voltage",
                "QA01:b1_gradient": "QA01:b1_gradient",
                "QA02:b1_gradient": "QA02:b1_gradient",
                "QE01:b1_gradient": "QE01:b1_gradient",
                "QE02:b1_gradient": "QE02:b1_gradient",
                "QE03:b1_gradient": "QE03:b1_gradient",
                "QE04:b1_gradient": "QE04:b1_gradient",
                }


# DirectoryOrCreate for archive and dashboard
archive_dir = f"{dir_path}/files/output/archive"
impact_archive_mount = MountPoint(
    name="archive_mount", host_path=archive_dir, mount_type="DirectoryOrCreate"
)

dashboard_dir = f"{dir_path}/files/output/dashboard"
dashboard_mount = MountPoint(
    name="dashboard_mount", host_path=dashboard_dir, mount_type="DirectoryOrCreate"
)


data = {
    "distgen_input_filename": distgen_input_filename,
    "distgen_output_filename": distgen_output_filename,
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

mount_points = [distgen_input_mount, distgen_output_mount, workdir_mount, impact_archive_input_mount, impact_archive_mount, dashboard_mount]

remote_modeling_service.predict(model_id=1, data=data, mount_points=mount_points, lume_configuration_file=LUME_CONFIGURATION_FILE)
