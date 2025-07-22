from setuptools import setup
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('scaper.version', 'scaper/version.py')
if spec is None or spec.loader is None:
    raise ImportError("Could not load spec or loader for 'scaper.version'")
version = importlib.util.module_from_spec(spec)
sys.modules['scaper.version'] = version
spec.loader.exec_module(version)


with open('README.md') as file:
    long_description = file.read()


setup(
    name='scaper',
    version=version.version,
    description='A library for soundscape synthesis and augmentation',
    author='Justin Salamon, Duncan MacConnell, David Grünert',
    author_email='justin.salamon@gmail.com',
    url='https://github.com/cyrta/dscaper',
    download_url='',
    packages=['scaper'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='audio sound soundscape environmental dsp mixing',
    license='BSD-3-Clause',
    classifiers=[
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Development Status :: 1 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Topic :: Multimedia :: Sound/Audio :: Analysis",
            "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
            "Programming Language :: Python :: 3.12",
        ],
    install_requires=[
        # 'sox',
        # 'jams',
        # 'numpy',
        # "soxbindings;platform_system!='Windows'",
        # 'pyloudnorm',
        # 'soundfile',
    ],
    extras_require={
        'docs': [
                'sphinx',  # autodoc was broken in 1.3.1
                'sphinx_rtd_theme',
                'sphinx_issues',
            ],
        'tests': ['backports.tempfile', 'pytest', 'pytest-cov', 'tqdm']
    }
)
