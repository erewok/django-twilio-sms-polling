from django.contrib import admin
from django import forms
from sms_app.models import Receiver, Messages, ResponseMessages, SentMessage, ReceivedMessage

class ReceiverForm(forms.ModelForm):
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', 
                                    error_message = ("Phone number must be entered in the format: \'+##########\'. Up to 15 digits allowed."))
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'age', 'city', 'timezone')
    form = ReceiverForm

class MessagesAdmin(admin.ModelAdmin):
    list_display = ('init_schedule_time','send_is_on', 'send_once', 'send_interval', 'stop_time', 'message_body')
    filter_horizontal = ('recipients',)
    # Fields: init_schedule_time, send_once, send_only_during_daytime, send_interval,
    # stop_time, recipients, message_body
    date_hierarchy = 'init_schedule_time'
    ordering = ('-init_schedule_time',)

class ResponseMessagesAdmin(admin.ModelAdmin):
    list_display = ('response_message', 'active')

class SentMessageAdmin(admin.ModelAdmin):
    list_display = ('msg_id', 'timestamp', 'to_number', 'conv_id', 'status')
    readonly_fields = ('msg_id',
                       'timestamp',
                       'to_number',
                       'conv_id',
                       'message_body',
                       'status')

class ReceivedMessageAdmin(admin.ModelAdmin):
    list_display = ('msg_id', 'timestamp', 'from_number', 'conv_id')
    readonly_fields = ('msg_id',
                       'timestamp',
                       'from_number',
                       'conv_id',
                       'message_body')

admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(ResponseMessages, ResponseMessagesAdmin)

admin.site.register(SentMessage, SentMessageAdmin)
admin.site.register(ReceivedMessage, ReceivedMessageAdmin)
