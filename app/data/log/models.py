from django.db import models as django
from django.utils.timezone import now

#from systems.command import messages
from systems.models import fields, environment, config
from data.user.models import User


class LogFacade(
    config.ConfigModelFacadeMixin,
    environment.EnvironmentModelFacadeMixin
):
    def default_order(self):
        return 'created'

    def get_display_fields(self):
        return (
            'name',
            'user', 
            'command',
            'status',
            '---', 
            'config',
            '---',
            'messages',
            '---',
            'created',
            'updated'
        )
    
    def get_field_user_display(self, value):
        return ('User', str(value))
    
    def get_field_command_display(self, value):
        return ('Command', value)
    
    def get_field_status_display(self, value):
        return ('Status', value)
    
    def get_field_messages_display(self, value):
        from systems.command import messages
        
        display = []
        for data in value:
            msg = messages.AppMessage.get(data, decrypt = False)
            display.append(msg.format(True))

        return ('Messages', "\n".join(display))
 

class Log(
    config.ConfigMixin,
    environment.EnvironmentModel
):
    user = django.ForeignKey(User, null=True, on_delete=django.PROTECT, related_name='+')
    command = django.CharField(max_length=256, null=True)
    status = django.CharField(max_length=64, null=True)
    messages = fields.EncryptedDataField(default=[])
        
    class Meta(environment.EnvironmentModel.Meta):
        facade_class = LogFacade

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.STATUS_SUCCESS = 'success'
        self.STATUS_FAILED = 'failed'

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "{}{}".format(
                now().strftime("%Y%m%d%H%M%S"),
                self.facade.generate_token(5)                
            )        
        super().save(*args, **kwargs)


    def success(self):
        return self.status == self.STATUS_SUCCESS
    
    def set_status(self, success):
        self.status = self.STATUS_SUCCESS if success else self.STATUS_FAILED
