# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Receiver'
        db.create_table(u'sms_receiver', (
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=17, primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('age', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal(u'sms', ['Receiver'])

        # Adding model 'SentMessage'
        db.create_table(u'sms_sentmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msg_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('to_number', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.Receiver'])),
            ('conv_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message_body', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'sms', ['SentMessage'])

        # Adding model 'ReceivedMessage'
        db.create_table(u'sms_receivedmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msg_id', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('from_number', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.Receiver'])),
            ('conv_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.SentMessage'])),
            ('message_body', self.gf('django.db.models.fields.TextField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'sms', ['ReceivedMessage'])

        # Adding model 'Messages'
        db.create_table(u'sms_messages', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('init_schedule_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('send_once', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('send_only_during_daytime', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('send_interval', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('stop_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('message_body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sms', ['Messages'])

        # Adding M2M table for field recipients on 'Messages'
        m2m_table_name = db.shorten_name(u'sms_messages_recipients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messages', models.ForeignKey(orm[u'sms.messages'], null=False)),
            ('receiver', models.ForeignKey(orm[u'sms.receiver'], null=False))
        ))
        db.create_unique(m2m_table_name, ['messages_id', 'receiver_id'])

        # Adding model 'ResponseMessages'
        db.create_table(u'sms_responsemessages', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('response_message', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal(u'sms', ['ResponseMessages'])

        # Adding model 'TwilioAcct'
        db.create_table(u'sms_twilioacct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account_sid', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('auth_token', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('our_number', self.gf('django.db.models.fields.CharField')(max_length=17)),
        ))
        db.send_create_signal(u'sms', ['TwilioAcct'])


    def backwards(self, orm):
        # Deleting model 'Receiver'
        db.delete_table(u'sms_receiver')

        # Deleting model 'SentMessage'
        db.delete_table(u'sms_sentmessage')

        # Deleting model 'ReceivedMessage'
        db.delete_table(u'sms_receivedmessage')

        # Deleting model 'Messages'
        db.delete_table(u'sms_messages')

        # Removing M2M table for field recipients on 'Messages'
        db.delete_table(db.shorten_name(u'sms_messages_recipients'))

        # Deleting model 'ResponseMessages'
        db.delete_table(u'sms_responsemessages')

        # Deleting model 'TwilioAcct'
        db.delete_table(u'sms_twilioacct')


    models = {
        u'sms.messages': {
            'Meta': {'object_name': 'Messages'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_schedule_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sms.Receiver']", 'symmetrical': 'False'}),
            'send_interval': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'send_once': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_only_during_daytime': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stop_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sms.receivedmessage': {
            'Meta': {'object_name': 'ReceivedMessage'},
            'conv_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sms.SentMessage']"}),
            'from_number': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sms.Receiver']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'msg_id': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'sms.receiver': {
            'Meta': {'object_name': 'Receiver'},
            'age': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '17', 'primary_key': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        u'sms.responsemessages': {
            'Meta': {'object_name': 'ResponseMessages'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response_message': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        u'sms.sentmessage': {
            'Meta': {'object_name': 'SentMessage'},
            'conv_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'msg_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'to_number': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sms.Receiver']"})
        },
        u'sms.twilioacct': {
            'Meta': {'object_name': 'TwilioAcct'},
            'account_sid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'auth_token': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'our_number': ('django.db.models.fields.CharField', [], {'max_length': '17'})
        }
    }

    complete_apps = ['sms']