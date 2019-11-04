import setuptools


setuptools.setup(
    name="ghia_svatozde", # Replace with your own username
    version="0.0.1",
    author="Zdenek Svaton",
    author_email="author@example.com",
    description="ghia webapp",
    long_description="""
        Simple app for consuming git webhooks.
    """,
    long_description_content_type="text/markdown",
    url="https://github.com/svatozde/ghia3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'flask',
        'click',
        'requests',
    ],
    python_requires='>=3.6',
    py_modules = ['ghia']
)