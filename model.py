from manager import BaseManager
from settings import DB_NAME


class Model:

    class Meta:
        DB = DB_NAME
        TABLE_NAME: str | None = None
        VERBOSE: bool = False
        PK_NAME: str = 'id'
        CREATE_TABLE: bool = False

    @classmethod
    def fields_definitions(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('_') and not callable(value) and not key == cls.Meta.PK_NAME}

    def fields(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and not callable(value) and not key == self.Meta.PK_NAME}

    @classmethod
    def table_name(cls):
        return cls.Meta.TABLE_NAME or cls.__name__.lower() + 's'

    @classmethod
    @property
    def manager(cls):
        return BaseManager(
            cls.Meta.DB, cls.table_name(), cls.fields_definitions(),
            pk_name=cls.Meta.PK_NAME, create_table=cls.Meta.CREATE_TABLE, verbose=cls.Meta.VERBOSE)

    @property
    def pk(self):
        return getattr(self, self.Meta.PK_NAME, None)

    def __init__(self, **kwargs):
        self._check_fields(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _check_fields(self, strict=True, **kwargs):
        if strict and len(kwargs) != len(self.fields_definitions()):
            raise ValueError(
                f'Invalid number of arguments expected {len(self.fields_definitions())} got {len(kwargs)}')
        for key in kwargs:
            if key not in self.fields_definitions():
                raise ValueError(f'Invalid field name {key}')

    @classmethod
    def setup(cls):
        with cls.manager as manager:
            manager.create_table()

    def save(self):
        fields = self.fields()
        self._check_fields(**fields)
        with self.manager as manager:
            if self.pk:
                manager.update(self.pk, **fields)
            else:
                pk = manager.insert(**fields)
                setattr(self, self.Meta.PK_NAME, pk)
        return self

    def update(self, **kwargs):
        self._check_fields(strict=False, **kwargs)
        with self.manager as manager:
            manager.update(self.pk, **kwargs)
            for key, value in kwargs.items():
                setattr(self, key, value)
            return self

    def delete_from_db(self):
        with self.manager as manager:
            manager.delete(self.pk)

    @classmethod
    def get(cls, pk: int):
        with cls.manager as manager:
            data = manager.get(pk)
            if data:
                obj = cls(**data[1])
                setattr(obj, cls.Meta.PK_NAME, data[0])
                return obj

    @classmethod
    def delete(cls, pk: int):
        with cls.manager as manager:
            return manager.delete(pk) == 1

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def list(cls, where=None, order=None, limit=None, offset=None):
        with cls.manager as manager:
            students = []
            for pk, data in manager.list(where, order, limit, offset):
                obj = cls(**data)
                setattr(obj, cls.Meta.PK_NAME, pk)
                students.append(obj)
            return students
