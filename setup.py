from distutils.core import setup
setup(name='timebox',
      version='0.2.1',
      package_dir = {'': 'package'},
      include_package_data=True,
      py_modules=['timebox', 'timeboximage', 'messages', 'utils/fonts', 'utils/gifreader'],
      )
