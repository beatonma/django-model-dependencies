"""

"""

import logging
from unittest import TestCase

from model_class_dependencies import (
    parse_models,
    parse_field,
    parse_field_params,
    build_model_references,
)

log = logging.getLogger(__name__)

SIMPLE_FIELD_PARAM = "max_length=6"
MULTI_FIELD_PARAM = "max_length=13, null=True"

SIMPLE_FIELD = " text = models.CharField(help_text='this is help text', max_length=255)"
MULTILINE_FIELD = """ text = models.CharField(
    max_length=160,
    help_text='this is multiline help text',
)"""

SIMPLE_FOREIGNKEY_FIELD = (
    " person = models.ForeignKey(Person, on_delete=models.CASCADE)"
)
STRING_FOREIGNKEY_FIELD = (
    " person = models.ForeignKey('Person', on_delete=models.CASCADE)"
)
MULTILINE_FOREIGNKEY_FIELD = """ constituency = models.ForeignKey(
    'Constituency',
    on_delete=models.DELETE,
    related_name='constituencies',
)"""

SIMPLE_MODEL = """class Simple(models.Model):
    text = models.CharField(max_length=255)

class SomethingElse:
    pass
"""

COMPLEX_MODEL = """class Bill(ParliamentDotUkMixin, BaseModel):
    title = models.CharField(max_length=512)
    description = models.CharField(max_length=1024)
    act_name = models.CharField(max_length=512)
    homepage = models.URLField()

    ballot_number = models.PositiveIntegerField(default=0)
    bill_chapter = models.PositiveIntegerField(default=0)

    is_private = models.BooleanField()

    bill_type = models.ForeignKey(
        'BillType',
        on_delete=models.CASCADE,
    )
    session = models.ForeignKey(
        'ParliamentarySession',
        on_delete=models.CASCADE,
        null=True,
        related_name='bills',
    )
"""

MULTIPLE_MODELS = """
class BillStageSitting(ParliamentDotUkMixin, BaseModel):
    bill_stage = models.ForeignKey(
        'BillStage',
        on_delete=models.DO_NOTHING,
        related_name='sittings',
    )
    date = models.DateField()
    formal = models.BooleanField()
    provisional = models.BooleanField()


class BillPublication(ParliamentDotUkMixin, BaseModel):
    bill = models.ForeignKey(
        'Bill',
        on_delete=models.DO_NOTHING,
    )
    title = models.CharField(max_length=512)


class Bill(ParliamentDotUkMixin, BaseModel):
    title = models.CharField(max_length=512)
    description = models.CharField(max_length=1024)
    act_name = models.CharField(max_length=512)
    homepage = models.URLField()

    ballot_number = models.PositiveIntegerField(default=0)
    bill_chapter = models.PositiveIntegerField(default=0)

    is_private = models.BooleanField()

    bill_type = models.ForeignKey(
        'BillType',
        on_delete=models.CASCADE,
    )
    session = models.ForeignKey(
        'ParliamentarySession',
        on_delete=models.CASCADE,
        null=True,
        related_name='bills',
    )
"""

MODEL_WITH_MIXIN = """class ParliamentDotUkMixin(models.Model):
    parliamentdotuk = models.PositiveIntegerField(
        primary_key=True,
        unique=True,
    )

    class Meta:
        abstract = True

class BillPublication(ParliamentDotUkMixin, BaseModel):
    bill = models.ForeignKey(
        'Bill',
        on_delete=models.DO_NOTHING,
    )
    title = models.CharField(max_length=512)
"""


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

    def test_parse_models(self):
        simple = parse_models(SIMPLE_MODEL)[0]
        self.assertEqual("Simple", simple.name)
        self.assertEqual("models.Model", simple.class_dependencies[0])

        complex = parse_models(COMPLEX_MODEL)[0]
        self.assertEqual(complex.name, "Bill")
        self.assertListEqual(
            complex.class_dependencies, ["ParliamentDotUkMixin", "BaseModel"]
        )
        self.assertEqual(len(complex.fields), 9)

        # bill_chapter = models.PositiveIntegerField(default=0)
        bill_chapter = complex.fields[5]
        self.assertEqual("bill_chapter", bill_chapter.name)
        self.assertEqual("models.PositiveIntegerField", bill_chapter.type)
        self.assertEqual([], bill_chapter.args)
        self.assertEqual("0", bill_chapter.kwargs["default"])

        self.assertListEqual(["BillType", "ParliamentarySession"], complex.fk_models())

        models = parse_models(MULTIPLE_MODELS)
        self.assertEqual(3, len(models))

        sitting, publication, bill = models
        self.assertEqual("BillStageSitting", sitting.name)
        self.assertEqual("BillPublication", publication.name)
        self.assertEqual("Bill", bill.name)

        self.assertEqual(4, len(sitting.fields))
        self.assertEqual(2, len(publication.fields))
        self.assertEqual(9, len(bill.fields))

    def test_mixin_inclusion(self):
        """If a model has mixins, and those mixins are discovered, then any fields
        from those mixins should be added to modelfields. """
        models = parse_models(MODEL_WITH_MIXIN)
        self.assertEqual(2, len(models))

        puk, publication = models
        self.assertEqual(2, len(publication.fields))

        build_model_references(models)
        puk, publication = models
        self.assertEqual(3, len(publication.fields))
        self.assertTrue('parliamentdotuk' in [x.name for x in publication.fields])
