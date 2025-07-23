from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from app.models import ClientStatusEnum, ClientTypeEnum

class AddClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Client name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    client_type = SelectField('Client Type', choices=[ (i.value, i.name.title()) for i in ClientTypeEnum], validators=[DataRequired()])
    status = SelectField('Status', choices=[ (i.value, i.name.title()) for i in ClientStatusEnum], validators=[DataRequired()])
    submit = SubmitField('Add Client')

class EditClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    client_type = SelectField('Client Type', choices=[ (i.value, i.value) for i in ClientTypeEnum], validators=[DataRequired()])
    status = SelectField('Status', choices=[ (i.value, i.value) for i in ClientStatusEnum], validators=[DataRequired()])
    submit = SubmitField('Update Client')