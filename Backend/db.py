import datetime
import hashlib
import os 
import bcrypt

from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

class User(db.model):
    """
    User Model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    #User Info 
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password_digest = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=True)

    #Session Information 
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    #Relationships 
    saved_recipes = db.relationship('SavedRecipe', back_populates='user')
    posts = db.relationship('Post', back_populates='author')
    comments = db.relationship('Comment', back_populates='user')
    memberships = db.relationship('GroupMembership', back_populates='user')



    def __init__(self, **kwargs):
        """
        Initializes a User Object
        """
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.username = kwargs.get("username")
        self.password_digest = bcrypt.hashpw(kwargs.get("password_digest")).encode("utf8"), bcrypt.gensalt(rounds=13).decode("utf8")
        self.renew_session() 

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions, i.e.
        1. Creates a new session token
        2. Sets the expiration time of the session to be a day from now
        3. Creates a new update token
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token
    
    def serialize(self):
        """
        Serializes the User object, including related data.
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "posts": [post.serialize() for post in self.posts],  
            "saved_recipes": [saved.recipe.serialize() for saved in self.saved_recipes],  
        }

    def simple_serialize(self):
        """
        Serializes the User object, without related data
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username
        }
    
class Recipe(db.model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)

    #Recipe Info
    title = db.Column(db.String, nullable=False)
    summary = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.JSON, nullable=False) 
    instructions = db.Column(db.JSON, nullable=False)
    image_url = db.Column(db.String, nullable=True)

    #Relationship
    saved_by = db.relationship('SavedRecipe', back_populates='recipe', lazy=True)

    def __init__(self, **kwargs):
        """
        Initializes a Recipe Object
        """
        self.title = kwargs.get("title")
        self.summary = kwargs.get("summary")
        self.ingredients = kwargs.get("ingredients")
        self.instructions = kwargs.get("instructions")

    def serialize(self):
        """
        Serializes the Recipe object 
        """
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "ingredients": self.ingredients if isinstance(self.ingredients, list) else self.ingredients.split('\n'),  # Handle JSON or plain string
            "instructions": self.instructions if isinstance(self.instructions, list) else self.instructions.split('\n')
        }
    
class SavedRecipe(db.model):
    __tablename__ = 'saved_recipes'
    id = db.Column(db.Integer, primary_key=True)

    #Saved Recipe info
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    
    #Relationship
    user = db.relationship('User', back_populates='saved_recipes')
    recipe = db.relationship('Recipe', back_populates='saved_by')


class Group(db.model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)

    #Group Info
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    image_url = db.Column(db.String, nullable=True)
    
    memberships = db.relationship('GroupMembership', back_populates='group')
    posts = db.relationship('Post', back_populates='group')


class GroupMembership(db.model):
    __tablename__ = 'group_memberships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    
    user = db.relationship('User', back_populates='memberships')
    group = db.relationship('Group', back_populates='memberships')

class Post(db.model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    
    author = db.relationship('User', back_populates='posts')
    group = db.relationship('Group', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post')

class Comment(db.model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    
    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

        



    
        



