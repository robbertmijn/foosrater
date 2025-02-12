from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class GameResultForm(FlaskForm):
    player_red1 = StringField('Player Red 1', validators=[DataRequired()])
    player_red2 = StringField('Player Red 2', validators=[DataRequired()])
    player_blue1 = StringField('Player Blue 1', validators=[DataRequired()])
    player_blue2 = StringField('Player Blue 2', validators=[DataRequired()])
    red_score = IntegerField('Red Goals', validators=[DataRequired()])
    blue_score = IntegerField('Blue Goals', validators=[DataRequired()])
    submit = SubmitField('Update Rating')

