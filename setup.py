from setuptools import setup, find_packages
setup(name='timebox',
      version='0.2.4',
      package_dir = {'': 'package'},
      packages=find_packages(include=['package/*.py']),
      include_package_data=True,
      py_modules=['timebox', 'timeboximage', 'messages', 'utils/fonts', 'utils/gifreader']
      )
