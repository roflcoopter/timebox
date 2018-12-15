from setuptools import setup
setup(name='timebox',
      version='0.1.1',
      package_dir = {'': 'package'},
      py_modules=['timebox', 'timeboximage', 'messages', 'utils/fonts', 'utils/gifreader'],
      data_files=[('timebox-fonts', ['examples/fonts/arcadeclassic.gif'])]
      )
