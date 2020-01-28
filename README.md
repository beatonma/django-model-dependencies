![Example output](example-output/example-output-complete.svg)

A tool to visualise relationships between Django Models in a project.

# Requirements

Dataclasses are used so Python 3.8 is required. This is a quick project I made
to use myself. If you want to use an older version of Python then you will need
to replace the Field and PyClass classes.

# Installation

    git clone https://github.com/beatonma/django-model-dependencies
    cd django-model-dependencies/

    # activate virtual environment here if you want

    # then
    python setup.py install

Then you can run it with:

    djmodgraph 'path/to/directory'

or to build a graph of the current directory:

    djmodgraph .

# Command line arguments
`--savas SAVEAS`: Save the graph to the given filename.  
`--models MODELS [MODELS ...]`: The output graph will show only these models and their direct relationships to other models.  
`-noshow`: Use alongside `--saveas` to bypass showing the image.  
`-nofields`: Ignore field-based relationships - ForeignKey, OneToOneField, ManyToManyField.  
`-nosubclass`: Ignore class inheritance-based relationships.  
`-noabstract`: Ignore abstract models (mixins, base model classes - anything with `class Meta: abstract = True`)  
`-fieldsonly`: Equivalent to `-noabstract -nosubclass`  
`-subclassonly`: Equivalent to `-nofields`  

# Testing

Clone the repo as above then run:

    python setup.py test
