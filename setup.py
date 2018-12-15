from setuptools import setup, find_packages
setup(name='timebox',
      version='0.2.4',
      packages=find_packages(exclude=['tests', 'tests.*'])
      include_package_data=True
      )
