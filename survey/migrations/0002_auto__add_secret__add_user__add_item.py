# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Secret'
        db.create_table(u'survey_secret', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('secret', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'survey', ['Secret'])

        # Adding model 'User'
        db.create_table(u'survey_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('email', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'survey', ['User'])

        # Adding model 'Item'
        db.create_table(u'survey_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.User'])),
            ('whenstored', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('batch', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('site', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('key', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal(u'survey', ['Item'])


    def backwards(self, orm):
        # Deleting model 'Secret'
        db.delete_table(u'survey_secret')

        # Deleting model 'User'
        db.delete_table(u'survey_user')

        # Deleting model 'Item'
        db.delete_table(u'survey_item')


    models = {
        u'survey.item': {
            'Meta': {'object_name': 'Item'},
            'batch': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
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
            'code': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['survey']