#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:58
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : database.py
# @Software: 富融钱通
# @Function: 数据库通用操作类

from .compat import basestring
from .extensions import db
import logging

logger = logging.getLogger(__name__)

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """
        Mixin that adds convenience methods for CRUD (create, read, update, delete) operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the hrt_api."""
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def all(cls):
        """
        查询所有的数据集合
        :return:
        """
        logger.debug(cls.__name__ + " all")
        return cls.query.all()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the hrt_api."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    def object_to_dict(self, fields):
        """
        获取对象的属性并返回
        :param fields: 属性名列表
        :return: key为属性名，value为属性值的字典
        """
        d = {}
        for k in fields:
            if hasattr(self, k):
                d[k] = getattr(self, k, '')
        return d


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, basestring) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.
    Usage: ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
