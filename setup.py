from setuptools import setup
import app


setup(
    name='calistra',
    version=app.__version__,
    packages=['app'],
    long_description=app.__doc__,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'calistra = app.main:start'
        ]
    }
)
