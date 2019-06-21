from setuptools import setup


with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
long_description=readme,
long_description_content_type='text/markdown',
)
