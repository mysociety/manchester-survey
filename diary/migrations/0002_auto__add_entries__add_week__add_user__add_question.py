# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Entries'
        db.create_table(u'diary_entries', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.Question'])),
            ('week', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.Week'])),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'diary', ['Entries'])

        # Adding model 'Week'
        db.create_table(u'diary_week', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('week', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'diary', ['Week'])

        # Adding model 'User'
        db.create_table(u'diary_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usercode', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('email', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('startdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('withdrawn', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'diary', ['User'])

        # Adding model 'Question'
        db.create_table(u'diary_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('for_week', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.Week'])),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'diary', ['Question'])


    def backwards(self, orm):
        # Deleting model 'Entries'
        db.delete_table(u'diary_entries')

        # Deleting model 'Week'
        db.delete_table(u'diary_week')

        # Deleting model 'User'
        db.delete_table(u'diary_user')

        # Deleting model 'Question'
        db.delete_table(u'diary_question')


    models = {
        u'diary.entries': {
            'Meta': {'object_name': 'Entries'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.User']"}),
            'week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Week']"})
        },
        u'diary.question': {
            'Meta': {'object_name': 'Question'},
            'for_week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Week']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'diary.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {}),
            'usercode': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'withdrawn': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'diary.week': {
            'Meta': {'object_name': 'Week'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'week': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['diary']