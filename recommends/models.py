from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from .converters import get_identifier
from .managers import RecommendsManager, SimilarityManager, RecommendationManager


class RecommendsBaseModel(models.Model):
    """(RecommendsBaseModel description)"""
    object_ctype = models.ForeignKey(ContentType, related_name="%(app_label)s_%(class)s_object_ctypes")
    object_id = models.PositiveIntegerField()
    object_site = models.ForeignKey(Site, related_name="%(app_label)s_%(class)s_object_sites")
    object = generic.GenericForeignKey('object_ctype', 'object_id')

    objects = RecommendsManager()

    class Meta:
        abstract = True
        unique_together = ('object_ctype', 'object_id', 'object_site')

    def __unicode__(self):
        return u"RecommendsBaseModel"

    def _object_identifier(self, ctype, object_id):
        obj = ctype.get_object_for_this_type(pk=object_id)
        return get_identifier(obj)

    def object_identifier(self):
        return self._object_identifier(self.object_ctype, self.object_id)


class Similarity(RecommendsBaseModel):
    """How much an object is similar to another"""

    score = models.FloatField(null=True, blank=True, default=None)

    related_object_ctype = models.ForeignKey(ContentType, related_name="%(app_label)s_%(class)s_related_object_ctypes")
    related_object_id = models.PositiveIntegerField()
    related_object_site = models.ForeignKey(Site, related_name="%(app_label)s_%(class)s_related_object_sites")
    related_object = generic.GenericForeignKey('related_object_ctype', 'related_object_id')

    objects = SimilarityManager()

    class Meta:
        verbose_name_plural = 'similarities'
        unique_together = ('object_ctype', 'object_id', 'object_site', 'related_object_ctype', 'related_object_id', 'related_object_site')
        ordering = ['-score']

    def __unicode__(self):
        return u"Similarity between %s and %s" % (self.get_object(), self.get_related_object())

    def related_object_identifier(self):
        return self._object_identifier(self.related_object_ctype, self.related_object_id)


class Recommendation(RecommendsBaseModel):
    """Recommended an object for a particular user"""
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_users")
    score = models.FloatField(null=True, blank=True, default=None)

    objects = RecommendationManager()

    class Meta:
        unique_together = ('object_ctype', 'object_id', 'user')
        ordering = ['-score']

    def __unicode__(self):
        return u"Recommendation for user %s" % (self.user)
