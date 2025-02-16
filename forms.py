from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import DataRequired

class GameResultForm(FlaskForm):
    red_score = SelectField('Red Score', choices=[(i, str(i)) for i in range(11)], coerce=int, validators=[DataRequired()])
    blue_score = SelectField('Blue Score', choices=[(i, str(i)) for i in range(11)], coerce=int, validators=[DataRequired()])
    
    player_red1 = StringField('Player Red 1', validators=[DataRequired()])
    player_red2 = StringField('Player Red 2')
    player_blue1 = StringField('Player Blue 1', validators=[DataRequired()])
    player_blue2 = StringField('Player Blue 2')

    date_time = DateTimeField('Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])

    submit = SubmitField('Add Game')

