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
