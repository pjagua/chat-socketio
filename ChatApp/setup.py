from setuptools import setup

setup(
    name='chatapp',
    version='0.1',
    packages=['chatapp'],
    author='Pedro J. Aguayo',
    author_email='pedro@aguayo.org',
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_socketio',
        'eventlet',
    ],
)
