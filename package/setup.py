from distutils.core import setup
setup(name='timebox',
      version='0.1',
      package_dir = {'': 'package'},
      package_data = {'examples/fonts': ['*']},
      py_modules=['timebox', 'timeboximage', 'messages', 'utils/fonts', 'utils/gifreader'],
      )
