"""
Setup script para instalación del paquete
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='promos-argentina',
    version='1.0.0',
    description='Sistema automatizado de scraping de promociones bancarias en supermercados de Argentina',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tu Nombre',
    author_email='paprikacasacrreativa@gmail.com',
    url='https://github.com/paprikacc/promos-argentina',
    project_urls={
        'Bug Reports': 'https://github.com/paprikacc/promos-argentina/issues',
        'Source': 'https://github.com/paprikacc/promos-argentina',
        'Documentation': 'https://github.com/paprikacc/promos-argentina#readme',
    },
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'playwright>=1.41.0',
        'beautifulsoup4>=4.12.2',
        'requests>=2.31.0',
        'python-dateutil>=2.8.2',
        'lxml>=4.9.3',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-playwright>=0.4.3',
            'black>=23.12.1',
            'flake8>=6.1.0',
            'mypy>=1.7.1',
        ],
        'analysis': [
            'pandas>=2.1.4',
            'openpyxl>=3.1.2',
            'matplotlib>=3.8.2',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Natural Language :: Spanish',
    ],
    keywords='argentina promociones supermercados scraping bancos descuentos',
    entry_points={
        'console_scripts': [
            'promos-scraper=scripts.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'promos-argentina': [
            'config/*.json',
            'data/.gitkeep',
            'data/cache/.gitkeep',
            'data/history/.gitkeep',
            'logs/.gitkeep',
        ],
    },
    zip_safe=False,
)
