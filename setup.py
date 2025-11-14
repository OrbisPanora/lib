import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='orbispanora-parser',
    version='0.1',
    author='OrbisPanora',
    description='An updated version of the anvil-parser2, parser for the Minecraft anvil file format, supports all Minecraft verions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://codefirst.iut.uca.fr/gitlab/IUT_INF63/projets-etudiants/OrbisPanora/lib',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'nbt',
        'frozendict',
    ],
    include_package_data=True
)
