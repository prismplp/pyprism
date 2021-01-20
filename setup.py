from setuptools import setup
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name='pyprism',
    version='1.0',
    packages=['pyprism'],
    entry_points={
        'console_scripts':[
            'pyprism = pyprism.main:main',
        ],
    },
    include_package_data=True,
    distclass=BinaryDistribution,
)
