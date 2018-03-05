from setuptools import setup
 

def requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list

setup(
    name='MongoDict', 
    version='0.1',
    packages=['MongoDict'],
    url='https://github.com/d-qoi/MongoDict.git',
    author='Alex Hirschfeld',
    author_email='alex@d-qoi.com',
    license='MIT',
    install_requires=requirements()
)
