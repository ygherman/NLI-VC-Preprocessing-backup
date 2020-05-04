from setuptools import setup

setup(
    name="VC_Preprocessing",
    version="1.1",
    packages=["data", "Database", "processes", "VC_collections"],
    url="https://github.com/ygherman/NLI-VC-Preprocessing",
    license="MIT",
    author="Yael Gherman",
    author_email="yael.vardinagherman@nli.org.il",
    description="preprocessing and ETL for NLI VC Catalogs",
    install_requires=[
        "pandas",
        "fuzzywuzzy",
        "oauth2client",
        "numpy",
        "gspread",
        "pymarc",
        "gooey",
        "mysql",
        "pony",
        "df2gspread",
        "dateutil",
    ],
)
