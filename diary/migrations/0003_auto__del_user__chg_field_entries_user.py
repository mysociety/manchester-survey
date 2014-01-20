# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'diary_user')


        # Changing field 'Entries.user'
        db.alter_column(u'diary_entries', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.User']))

    def backwards(self, orm):
        # Adding model 'User'
        db.create_table(u'diary_user', (
            ('startdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('usercode', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('email', self.gf('django.db.models.fields.TextField')(unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('withdrawn', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'diary', ['User'])


        # Changing field 'Entries.user'
        db.alter_column(u'diary_entries', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.User']))

    models = {
        u'diary.entries': {
            'Meta': {'object_name': 'Entries'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.User']"}),
            'week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Week']"})
        },
        u'diary.question': {
            'Meta': {'object_name': 'Question'},
            'for_week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Week']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optional': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'diary.week': {
            'Meta': {'object_name': 'Week'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'week': ('django.db.models.fields.IntegerField', [], {})
        },
        u'survey.user': {
            'Meta': {'object_name': 'User'},
            'code': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {}),
            'withdrawn': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['diary']