# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Question'
        db.delete_table(u'diary_question')


        # Renaming column for 'Entries.question' to match new field type.
        db.rename_column(u'diary_entries', 'question_id', 'question')
        # Changing field 'Entries.question'
        db.alter_column(u'diary_entries', 'question', self.gf('django.db.models.fields.TextField')())
        # Removing index on 'Entries', fields ['question']
        db.delete_index(u'diary_entries', ['question_id'])


    def backwards(self, orm):
        # Adding index on 'Entries', fields ['question']
        db.create_index(u'diary_entries', ['question_id'])

        # Adding model 'Question'
        db.create_table(u'diary_question', (
            ('optional', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('for_week', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.Week'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'diary', ['Question'])


        # Renaming column for 'Entries.question' to match new field type.
        db.rename_column(u'diary_entries', 'question', 'question_id')
        # Changing field 'Entries.question'
        db.alter_column(u'diary_entries', 'question_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['diary.Question']))

    models = {
        u'diary.entries': {
            'Meta': {'object_name': 'Entries'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.User']"}),
            'week': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['diary.Week']"})
        },
        u'diary.week': {
            'Meta': {'object_name': 'Week'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'week': ('django.db.models.fields.IntegerField', [], {})
        },
        u'survey.user': {
            'Meta': {'object_name': 'User'},
            'code': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'token': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'withdrawn': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['diary']