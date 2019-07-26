from setuptools import setup, find_packages

with open('README.rst', 'r') as fh:
    long_desc = fh.read()

setup(name='miqa_worker_task',
      version='0.0.1',
      description='Miqa active learning task',
      long_description=long_desc,
      author='Kitware Inc',
      author_email='kitware@kitware.com',
      license='MIT license',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python'
      ],
      install_requires=[
          'girder_worker',
          'girder_worker_utils'
          # TODO: Add additional packages required by both
          # producer and consumer side installations
      ],
      extras_require={
          'girder': [
              # TODO: Add dependencies here that are required for the
              # package to work on the producer (Girder) side.
          ],
          'worker': [
              # TODO: Add dependencies here that are required for the
              # package to work on the consumer (Girder Worker) side.
          ]
      },
      include_package_data=True,
      entry_points={
          'girder_worker_plugins': [
              'miqa_worker_task = miqa_worker_task:MiqaWorkerTask',
          ]
      },
      packages=find_packages(),
      zip_safe=False)
