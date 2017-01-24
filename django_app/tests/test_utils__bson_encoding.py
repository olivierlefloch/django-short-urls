# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase
from utils import bson_encoding


class BsonEncodingTestCase(PyW4CTestCase):

    def test_encode_field_name(self):
        self.assertEqual(bson_encoding.encode_field_name('azerty'), 'azerty')
        self.assertEqual(bson_encoding.encode_field_name('az.rty'), 'az%46rty')
        self.assertEqual(bson_encoding.encode_field_name('az$rty'), 'az%36rty')
        self.assertEqual(bson_encoding.encode_field_name('az%rty'), 'az%37rty')
        self.assertEqual(bson_encoding.encode_field_name('az%.$rty'), 'az%37%46%36rty')

    def test_decode_field_name(self):
        self.assertEqual(bson_encoding.decode_field_name('azerty'), 'azerty')
        self.assertEqual(bson_encoding.decode_field_name('az%46rty'), 'az.rty')
        self.assertEqual(bson_encoding.decode_field_name('az%36rty'), 'az$rty')
        self.assertEqual(bson_encoding.decode_field_name('az%37rty'), 'az%rty')
        self.assertEqual(bson_encoding.decode_field_name('az%37%46%36rty'), 'az%.$rty')

    def test_encode_decode(self):
        self.assertEqual(
            bson_encoding.decode_field_name(bson_encoding.encode_field_name('azertyuiop&é"56ù:')),
            'azertyuiop&é"56ù:'
        )
        self.assertEqual(bson_encoding.decode_field_name(bson_encoding.encode_field_name('.$%%$.')), '.$%%$.')

    def test_encode_dict(self):
        self.assertEqual(bson_encoding.encode_dict('to.to'), 'to.to')
        self.assertEqual(bson_encoding.encode_dict({'to.to': 'titi'}), {'to%46to': 'titi'})
        self.assertEqual(bson_encoding.encode_dict({'to.to': {'te.te': 'titi'}}), {'to%46to': {'te%46te': 'titi'}})
        self.assertEqual(bson_encoding.encode_dict({'to$to': {'te%te': 'titi'}}), {'to%36to': {'te%37te': 'titi'}})

    def test_decode_dict(self):
        self.assertEqual(bson_encoding.decode_dict('to%46to'), 'to%46to')
        self.assertEqual(bson_encoding.decode_dict({'to%46to': 'titi'}), {'to.to': 'titi'})
        self.assertEqual(bson_encoding.decode_dict({'to%46to': {'te%46te': 'titi'}}), {'to.to': {'te.te': 'titi'}})
        self.assertEqual(bson_encoding.decode_dict({'to%36to': {'te%37te': 'titi'}}), {'to$to': {'te%te': 'titi'}})

    def test_encode_decode_dict(self):
        self.assertEqual(
            bson_encoding.decode_dict(bson_encoding.encode_dict({'to$to': {'te%te': {'tu.tu': 'titi'}}})),
            {'to$to': {'te%te': {'tu.tu': 'titi'}}}
        )
