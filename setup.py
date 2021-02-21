from setuptools import setup, find_packages

setup(
    name="fuel-logger",
    use_scm_version=True,
    author="travipross",
    packages=find_packages(),
    setup_requires=["setuptools_scm"],
    install_requires=[
        'python-dotenv',
        'email-validator',
        'flask',
        'flask-bootstrap',
        'flask-login',
        'flask-mail',
        'flask-migrate',
        'flask-moment',
        'flask-sqlalchemy',
        'flask-wtf',
        'pandas',
        'pyjwt'
    ]
)