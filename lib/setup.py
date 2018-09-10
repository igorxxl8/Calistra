from setuptools import setup, find_packages
import calistra_lib

setup(
    name='calistra_lib',
    version=calistra_lib.__version__,
    packages=find_packages(),
    long_description="lib",
    include_package_data=True,
    test_suite='test', install_requires=['django']
)
