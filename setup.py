import setuptools
import codecs
from glob import glob


with codecs.open("README.md",encoding='utf-8') as fh:
    long_description = fh.read()

with codecs.open("LICENSE",encoding='utf-8') as fh:
    license = fh.read()


packages = setuptools.find_packages(include=['ghia'])

setuptools.setup(
    name="ghia_svatozde", # Replace with your own username
    version="0.0.17",
    author="Zdenek Svaton",
    author_email="author@example.com",
    description="ghia webapp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svatozde/ghia3",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'flask',
        'click',
        'requests',
    ],
    license = license,
    python_requires='>=3.6',
    packages=packages,
    data_files=[
        ('', glob('data/**'))
    ],
    entry_points={  # Optional
        'console_scripts': [
            'ghia=ghia.__main__:main',
        ],
    },
)