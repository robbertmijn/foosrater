from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class GameResultForm(FlaskForm):
    player_red1 = StringField('Player Red 1', validators=[DataRequired()])
    player_red2 = StringField('Player Red 1', validators=[DataRequired()])
    player_blue1 = StringField('Player Blue 1', validators=[DataRequired()])
    player_blue2 = StringField('Player Blue 2', validators=[DataRequired()])
    # outcome = SelectField('Outcome', choices=[('win', 'Red team wins'), ('lose', 'Blue team wins'), ('draw', 'Draw')], validators=[DataRequired()])
    goals_red = StringField('Red Goals', validators=[DataRequired()])
    goals_blue = StringField('Blue Goals', validators=[DataRequired()])
    submit = SubmitField('Update Rating')

