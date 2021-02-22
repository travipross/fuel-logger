from fuel_logger import ma 
from fuel_logger.models import User

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    
    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()

user_schema = UserSchema()
users_schema = UserSchema(many=True)
