from setuptools import setup, find_packages
from os import path, environ
import versioneer

cur_dir = path.abspath(path.dirname(__file__))

# parse requirements
with open(path.join(cur_dir, "requirements.txt"), "r") as f:
    requirements = f.read().split()



setup(
    name="slac_services",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="SLAC National Accelerator Laboratory",
    author_email="jgarra@slac.stanford.edu",
    license="SLAC Open",
    packages=find_packages(),
    install_requires=requirements,
    # set up development requirements
    extras_require={
        "test": ["pytest"],
    },
    url="https://github.com/slaclab/slac_services",
    include_package_data=True,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'save-model = slac_services.scripts.models:save_model',
            'save-model-deployment = slac_services.scripts.models:save_model_deployment',
            'create-project = slac_services.scripts.models:create_project',
            'save-deployment-flow = slac_services.scripts.models:save_deployment_flow'
        ]
    },
)
