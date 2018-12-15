from setuptools import setup, find_packages
setup(name='timebox',
      version='0.1',
      package_dir = {'': 'package'},
      include_package_data=True,
      py_modules=['timebox', 'timeboximage', 'messages', 'utils/fonts', 'utils/gifreader'],
      )
