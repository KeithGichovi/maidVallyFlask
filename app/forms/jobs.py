from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, DateTimeField, DecimalField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from app.models import Client, JobType, ClientStatusEnum
from datetime import datetime


class AddJobForm(FlaskForm):
    client_id = SelectField('Client', validators=[DataRequired()], coerce=int)
    job_type_id = SelectField('Job Type', validators=[DataRequired()], coerce=int)
    total_amount = DecimalField('Amount Charging', validators=[DataRequired()], default=0.0, rounding=None, places=2)
    time_started = DateTimeField('Time Started', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    time_ended = DateTimeField('Time Ended', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    location = StringField('Location')
    description = TextAreaField('Description')
    submit = SubmitField('Add Job')
    
    def __init__(self, *args, **kwargs):

        super(AddJobForm, self).__init__(*args, **kwargs)
        
        # Get active clients dynamically
        active_clients = Client.query.filter_by(status=ClientStatusEnum.ACTIVE).all()
        self.client_id.choices = [(0, 'Select a client...')] + [
            (client.id, client.name) for client in active_clients
        ]
        
        # Get job types dynamically
        job_types = JobType.query.all()
        self.job_type_id.choices = [(0, 'Select a job type...')] + [
            (job_type.id, job_type.name) for job_type in job_types
        ]

    def validate_time_started(self, field):
        """Validate that start time is not in the future"""
        if field.data and field.data > datetime.now():
            raise ValidationError("Start time must be in the past or present.")

    def validate_time_ended(self, field):
        """Validate that end time is not in the future and is after start time"""
        if field.data and field.data > datetime.now():
            raise ValidationError("End time must be in the past or present.")
        
        # Check if start time exists and end time is after start time
        if self.time_started.data and field.data and field.data <= self.time_started.data:
            raise ValidationError("End time must be after start time.")

    def validate_client_id(self, field):
        """Validate that a client was selected"""
        if field.data == 0:
            raise ValidationError("Please select a client.")

    def validate_job_type_id(self, field):
        """Validate that a job type was selected"""
        if field.data == 0:
            raise ValidationError("Please select a job type.")
        
    def validate_amount_below_zero(self, field):
        if field.data < 0:
            raise ValidationError("Amount cannot be negative.")
        