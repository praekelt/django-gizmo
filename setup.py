from setuptools import setup, find_packages

setup(
    name='django-gizmo',
    version='dev',
    description='Django app allowing for configurable targetting of template inclusion tags.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/django-gizmo',
    packages = find_packages(),
    include_package_data=True,
)
