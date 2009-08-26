"""
validatorselecter Module

this contains the class which allows the ViewConfig to select the appropriate validator for the given field

Classes:
Name                               Description
ValidatorSelecter                     Parent Class
SAValidatorSelector                   Selecter Based on sqlalchemy field types
DatabaseViewValidatorSelector         Database View always selects the same validator
TableDefValidatorSelector             Table def fields use the same validator

Exceptions:
None

Functions:
None


Copyright (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import *
from sqlalchemy.types import String as StringType
from tw.forms.validators import *
from formencode.compound import All
from formencode import Invalid
from formencode.validators import StringBool
from sqlalchemy.orm import PropertyLoader, SynonymProperty

class ValidatorSelector(object):
    _name_based_validators = {}

    def __new__(cls, *args, **kw):
        bases = cls.mro()
        chained_attrs = ['_name_based_validators']
        for base in bases:
            for attr in chained_attrs:
                if hasattr(base, attr):
                    current =  getattr(cls, attr)
                    current.update(getattr(base, attr))
        return object.__new__(cls, *args, **kw)

    def __getitem__(self, field):
        return self.select(field)

    def __init__(self, *args, **kw):
        pass

    @property
    def name_based_validators(self):
        validators = self._do_get_name_based_validators()
        validators.update(self._name_based_validators)
        return validators

    def select(self, field):
        return UnicodeString

    def _do_get_name_based_validators(self):
        return {}

class MongoKitValidatorSelector(ValidatorSelector):
    pass

class SAValidatorSelector(ValidatorSelector):

    default_validators = {
    StringType:   UnicodeString,
    Integer:  Int,
    Numeric:  Number,
    DateTime: DateValidator,
    Date:     DateValidator,
    Time:     DateValidator,
#    Binary:   UnicodeString,
    PickleType: UnicodeString,
#    Boolean: UnicodeString,
#    NullType: TextField
    }

    _name_based_validators = {'email_address':Email}

    def __init__(self, provider):
        self.provider = provider

    def select(self, field):

        if isinstance(field, PropertyLoader):
            return

        if isinstance(field, SynonymProperty):
            return

        #do not validate boolean or binary arguments
        if isinstance(field.type, (Boolean, Binary)):
            return None

        if field.name in self.name_based_validators:
            return self.name_based_validators[field.name]

        type_ = StringType
        for t in self.default_validators.keys():
            if isinstance(field.type, t):
                type_ = t
                break

        validator_type = self.default_validators[type_]

        return validator_type
