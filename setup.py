from setuptools import find_packages, setup

setup(
    name="fuel-logger",
    use_scm_version=True,
    author="travipross",
    packages=find_packages(),
    include_package_data=True,
    setup_requires=["setuptools_scm"],
    install_requires=[
        "python-dotenv",
        "email-validator",
        "flask<3",
        "flask-bootstrap",
        "flask-cors",
        "flask-httpauth",
        "flask-login",
        "flask-mail",
        "flask-marshmallow",
        "flask-migrate",
        "flask-moment",
        "flask-sqlalchemy",
        "flask-wtf",
        "marshmallow-sqlalchemy",
        "pandas",
        "pyjwt",
    ],
    entry_points={"console_scripts": ["fuel-logger = fuel_logger.fuel_logger:wsgi"]},
)
