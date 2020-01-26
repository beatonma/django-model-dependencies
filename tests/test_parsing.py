"""
Run with `nosetests --traverse-namespace`
"""

import logging
from unittest import TestCase

from model_class_dependencies import (
    inherit_mixin_fields,
    parse_field,
    parse_field_params,
    parse_classes,
)
from .data.data_parsing import *

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class ParsingTests(TestCase):
    def test_parse_field_params(self):
        args, kwargs = parse_field_params(SIMPLE_FIELD_PARAM)
        self.assertEqual([], args)
        self.assertEqual(kwargs["max_length"], "6")

    def test_parse_field(self):
        simple = parse_field(SIMPLE_FIELD)
        self.assertEqual("text", simple.name)
        self.assertEqual("models.CharField", simple.type)
        self.assertEqual([], simple.args)
        self.assertEqual(simple.kwargs["max_length"], "255")

        multiline = parse_field(MULTILINE_FIELD)
        self.assertEqual("text", multiline.name)
        self.assertEqual("models.CharField", multiline.type)
        self.assertEqual(multiline.kwargs["help_text"], "this is multiline help text")

    def test_parse_foreignkey_field(self):
        # ForeignKey with a class passed as the actual class, not a string name.
        simple = parse_field(SIMPLE_FOREIGNKEY_FIELD)
        self.assertEqual("person", simple.name)
        self.assertEqual("models.ForeignKey", simple.type)

        self.assertEqual("Person", simple.args[0])
        self.assertEqual(simple.kwargs["on_delete"], "models.CASCADE")

        # ForeignKey with a class passed by string name
        stringfk = parse_field(STRING_FOREIGNKEY_FIELD)
        self.assertEqual("person", simple.name)
        self.assertEqual("models.ForeignKey", simple.type)

        self.assertEqual("Person", stringfk.args[0])
        self.assertEqual(stringfk.kwargs["on_delete"], "models.CASCADE")

        # ForeignKey spread across several lines
        multiline = parse_field(MULTILINE_FOREIGNKEY_FIELD)
        self.assertEqual("constituency", multiline.name)
        self.assertEqual("models.ForeignKey", multiline.type)

        self.assertEqual("Constituency", multiline.args[0])
        self.assertEqual(multiline.kwargs["on_delete"], "models.DELETE")
        self.assertEqual(multiline.kwargs["related_name"], "constituencies")

    def test_parse_classes(self):
        simple = parse_classes(SIMPLE_MODEL)["Simple"]
        self.assertEqual("Simple", simple.name)
        self.assertEqual("models.Model", simple.class_dependencies[0])

        _complex = parse_classes(COMPLEX_MODEL)["Bill"]
        self.assertListEqual([], _complex.foreign_key_fields())

        _complex.is_model = True
        self.assertListEqual(
            ["ParliamentDotUkMixin", "BaseModel"],
            _complex.class_dependencies
        )
        self.assertEqual(len(_complex.fields), 9)

        bill_chapter = _complex.fields[5]
        self.assertEqual("bill_chapter", bill_chapter.name)
        self.assertEqual("models.PositiveIntegerField", bill_chapter.type)
        self.assertEqual([], bill_chapter.args)
        self.assertEqual("0", bill_chapter.kwargs["default"])

        self.assertListEqual(
            ["BillType", "ParliamentarySession"],
            _complex.foreign_key_models()
        )

        models = parse_classes(MULTIPLE_MODELS)
        self.assertEqual(3, len(models.values()))

        sitting = models["BillStageSitting"]
        publication = models["BillPublication"]
        bill = models["Bill"]

        self.assertEqual(4, len(sitting.fields))
        self.assertEqual(2, len(publication.fields))
        self.assertEqual(9, len(bill.fields))

    def test_inherit_mixin_fields(self):
        """If a model has mixins, and those mixins are discovered, then any fields
        from those mixins should be added to modelfields. """
        models = parse_classes(MODEL_WITH_MIXIN)
        for x in models.values():
            x.is_model = True

        self.assertEqual(3, len(models.values()))

        publication = models["BillPublication"]
        self.assertEqual(2, len(publication.fields))

        inherit_mixin_fields(models)

        self.assertEqual(3, len(publication.fields))
        self.assertTrue('parliamentdotuk' in [x.name for x in publication.fields])

        print(publication.foreign_key_models())
        self.assertTrue('Bill' in publication.foreign_key_models())
