from setuptools import setup

setup(name='c3d2OSIM',
      version='0.1',
      description='C3D to OpenSim converter tool',
      url='https://github.com/dvarnai/pyC3D2OSIM',
      author='Daniel Varnai',
      author_email='dvarnai@hotmail.com',
      license='MIT',
      packages=['c3d2OSIM'],
      install_requires=[
          'c3d',
          'numpy',
          'scipy',
          'pandas'
      ],
      zip_safe=False)