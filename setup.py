from setuptools import setup

setup(name='FluidSeg',
      version='0.1',
      description='Chinese segmentation with fluid granularity',
      url='http://github.com/seantyh/fluidSeg',
      author='Sean Tseng',
      author_email='seantyh@gmail.com',
      license='GNUv3',
      packages=['fluidSeg'],
      test_suite='tests',
      zip_safe=False)