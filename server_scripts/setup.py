from setuptools import setup

setup(
    name='server_scripts',
    version='1',
    author='Robert Hickman',
    author_email='robehickman@gmail.com',
    license='MIT',
    install_requires=[
        'pymysql',
        'pyyaml',
    ],
    packages=['srvmanage_core'],
    scripts=['scripts/srvmanage.py', 'scripts/backup_mysql.py'],
    zip_safe=False)
