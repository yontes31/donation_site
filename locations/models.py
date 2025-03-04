# Create your models here.
from django.db import models
import json

class DonationCategory(models.Model):
    name_hebrew = models.CharField(max_length=100)   # Example: 'ביגוד'
    name_english = models.CharField(max_length=100)  # Example: 'clothing'
    keywords = models.TextField(help_text="מילות חיפוש עבור ה-API, מופרדות בפסיקים")

    class Meta:
        verbose_name = "קטגוריית תרומה"
        verbose_name_plural = "קטגוריות תרומה"

    def __str__(self):
        return self.name_hebrew

class Location(models.Model):
    name  = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    opening_hours = models.TextField()

class DonationLocation(models.Model):
    name = models.CharField(max_length=200, verbose_name="שם המקום")
    address = models.TextField(verbose_name="כתובת")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="טלפון")
    website = models.URLField(blank=True, null=True, verbose_name="אתר אינטרנט")
    categories = models.ManyToManyField(DonationCategory, verbose_name="קטגוריות")
    opening_hours = models.TextField(blank=True, null=True, verbose_name="שעות פתיחה")
    google_place_id = models.CharField(max_length=100, unique=True)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="עודכן לאחרונה")
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    upvotes = models.IntegerField(default=0, verbose_name="הצבעות חיוביות")
    downvotes = models.IntegerField(default=0, verbose_name="הצבעות שליליות")

    def __str__(self):
        return self.name

    @property
    def score(self):
        """Calculate the score (upvotes - downvotes)"""
        return self.upvotes - self.downvotes

    @property
    def total_votes(self):
        """Calculate the total number of votes"""
        return self.upvotes + self.downvotes

def format_opening_hours(self):
    """
    Formats opening hours data into a human-readable string.

    Returns:
        str: A string representing the formatted opening hours.
    """

    if not self.opening_hours:
        return "No opening hours available"

    try:
        hours_data = json.loads(self.opening_hours) 
    except json.JSONDecodeError:
        return "Invalid opening hours format"

    formatted_hours = ""
    for day, hours in hours_data.get('weekday_text', {}).items():
        formatted_hours += f"{day.capitalize()}: {hours}\n" 

    return formatted_hours

class Posts(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)

    def __str__(self):
        return self.title