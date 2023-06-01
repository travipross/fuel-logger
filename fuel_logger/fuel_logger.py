from fuel_logger import create_app, db
from fuel_logger.models import Fillup, User, Vehicle

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Vehicle": Vehicle,
        "Fillup": Fillup,
        "v": Vehicle.query.first(),
        "u": User.query.first(),
    }


def wsgi():
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    wsgi()
