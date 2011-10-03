from django.db import models
from django.db.models.base import ModelBase


class EmptyObject(object):
    pass


class MetaBehavior(ModelBase):
    """
    Base Metaclass for Behaviors
    """
    def __new__(cls, name, bases, attrs):
        """
        This allows declarative field definition in behaviors, just like in a
        regular model definition, while still allowing field names to be
        customized. Given a behavior::

            class FooBehavior(Behavior):
                some_column = IntegerField()

        A child class declaring::

            class MyModel(FooBehavior):
                class FooBehavior:
                    some_column = 'another_name'

        will be able to change the name of some_column to another_name.

        To do this, we rip out all instances of model.Field, and wait for
        Behavior.modify_schema to add them back in once all config classes are
        merged.
        """

        declared_fields = {}

        for property_name in attrs:
            if isinstance(attrs[property_name], models.Field):
                declared_fields[property_name] = attrs[property_name]
        for field in declared_fields:
            del attrs[field]

        attrs['declared_fields'] = declared_fields

        new_class = super(MetaBehavior, cls).__new__(cls, name, bases, attrs)
        new_class.merge_parent_settings()
        if not new_class._meta.abstract:
            # non-abstract classes can't have their field overridden
            for field_name in declared_fields:
                new_class.add_to_class(field_name, declared_fields[field_name])
            new_class.modify_schema()
        else:
            # make sure abstract classes have an inner settings class
            if not hasattr(new_class, new_class.__name__):
                setattr(new_class, new_class.__name__, EmptyObject())

        return new_class

class Behavior(models.Model):
    """
    Base class for all Behaviors

    Behaviors are implemented through model inheritance, and support
    multi-inheritance as well.  Each behavior adds a set of default fields
    and/or methods to the model.  Field names can be customized like example B.

    EXAMPLE A
    class MyModel(FooBehavior):
        pass

    MyModel will have whatever fields FooBehavior adds with default field
    names.

    EXAMPLE B
    class MyModel(FooBehavior):
        class FooBehavior:
            bar = "qux"
            baz = "quux"

    MyModel will have the fields from FooBehavior added, but the field names
    will be "qux" and "quux" respectively.

    EXAMPLE C
    class MyModel(FooBehavior, BarBehavior):
        pass

    MyModel will have the fields from both FooBehavior and BarBehavior, each
    with default field names.  To customizing field names can be done just like
    it was in example B.

    """
    class Meta:
        abstract = True
    __metaclass__ = MetaBehavior


    @classmethod
    def modify_schema(cls):
        """
        Hook for behaviors to modify their model class just after it's created
        """

        # Everything in declared_fields was pulled out by our metaclass, time
        # to add them back in
        for parent in cls.mro():
            try:
                declared_fields = parent.declared_fields
            except AttributeError:  # Model itself doesn't have declared_fields
                continue

            for name, field in declared_fields.iteritems():
                new_name = getattr(getattr(cls, parent.__name__, EmptyObject()), name, name)
                if not hasattr(cls, new_name):
                    cls.add_to_class(new_name, field)


    @classmethod
    def merge_parent_settings(cls):
        """
        Every behavior's settings are stored in an inner class whose name
        matches its behavior's name. This method implements inheritance for
        those inner classes.
        """
        behaviors = [behavior.__name__ for behavior in cls.base_behaviors()]
        for parent in cls.mro():
            for behavior in behaviors:
                parent_settings = dict(getattr(parent, behavior, EmptyObject()).__dict__)
                child_settings = getattr(cls, behavior, EmptyObject()).__dict__
                parent_settings.update(child_settings)
                getattr(cls, behavior).__dict__ = parent_settings

    @classmethod
    def base_behaviors(cls):
        behaviors = []
        for parent in cls.mro():
            if hasattr(parent, parent.__name__):
                behaviors.append(parent)
        return behaviors


class TimeStampable(Behavior):
    """
    Base class for adding timestamping behavior to a model.

    Added Fields:
        Field 1:
            field: DateTimeField(auto_now_add=True)
            description: Timestamps set at the creation of the instance
            default_name: created_at
        Field 2:
            field: DateTimeField(auto_now_add=True)
            description: Timestamps set each time the save method is called on the instance
            default_name: updated_at

    """
    class Meta:
        abstract = True

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class SEO(Behavior):
    """
    Base class for adding seo behavior to a model.

    Added Fields:
        Field 1:
            field: CharField(max_length = 255)
            description: Char field intended for use in html <title> tag.
            validation: Max Length 255 Characters
            default_name: seo_title
        Field 2:
            field: TextField()
            description: Text field intended for use in html <meta name="description"> tag.
            default_name: seo_description
        Field 3:
            field: TextField()
            description: Text field intended for use in html <meta name="keywords"> tag.
            validation: comma separated text strings
            default_name: seo_keywords

    """
    class Meta:
        abstract = True

    seo_title = models.CharField(max_length = 255)
    seo_description = models.TextField()
    seo_keywords = models.TextField()
