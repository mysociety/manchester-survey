# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'User.code'
        db.delete_column(u'survey_user', 'code')


    def backwards(self, orm):
        # Adding field 'User.code'
        db.add_column(u'survey_user', 'code',
                      self.gf('django.db.models.fields.TextField')(default='', unique=True, db_index=True),
                      keep_default=False)


    models = {
        u'survey.item': {
            'Meta': {'object_name': 'Item'},
            'batch': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.User']"}),
            'value': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'whenstored': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'survey.secret': {
            'Meta': {'object_name': 'Secret'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.TextField', [], {})
        },
        u'survey.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'withdrawn': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['survey']