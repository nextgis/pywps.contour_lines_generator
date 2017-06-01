from setuptools import setup, find_packages

version = '0.0'

setup(
    name='avral',
    version=version,
    description="",
    long_description="""""",
    classifiers=[],
    keywords='',
    author='Aleksandr Lisovenko',
    author_email='alexander.lisovenko@gmail.com',
    url='',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pywps',
        'owslib',
        'flask',
    ],
    # entry_points={
    #     'console_scripts': [ 'osmshp = osmshp.script:main', ],
    # },
)