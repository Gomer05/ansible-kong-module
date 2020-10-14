from setuptools import setup

files = [
    "ansible/modules/kong",
    "ansible/module_utils/kong",
]

long_description = open('README.md', 'r').read()
version = open('VERSION', 'r').read()

setup(
    name='ansible-modules-kong',
    version=version,
    description='Ansible Modules for Kong 1.5.x.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mark Persohn',
    author_email='mark@planetfind.com',
    url='https://github.com/Gomer05/ansible-kong-module',
    packages=files,
    install_requires=['ansible>=2.9.0', 'ansible-dotdiff'],
)
