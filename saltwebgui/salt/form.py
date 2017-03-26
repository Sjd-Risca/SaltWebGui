"""Form for flask-wtform"""
#pylint: disable=line-too-long
from flask_wtf import Form
from wtforms import StringField, RadioField, SubmitField #BooleanField

class FormHighstate(Form):
    """For running a highstate job"""
    #pylint: disable=no-init,too-few-public-methods
    target = StringField('Target the minions')
    test_mode = RadioField('test', choices=[('True', 'True'),
                                            ('False', 'False')],
                           default='True')
    submit = SubmitField('Run highstate',
                         render_kw={"class": "btn btn-success"})

class FormSalt(Form):
    """Form for running saltstack commands."""
    #pylint: disable=no-init,too-few-public-methods
    target = StringField('Target the minions')
    command = StringField('Type the saltstack command to run (like "cmd.run whoami")')
    test_mode = RadioField('test', choices=[('True', 'True'),
                                            ('False', 'False')],
                           default='True')
    submit = SubmitField('Run command',
                         render_kw={"class": "btn btn-success"})

