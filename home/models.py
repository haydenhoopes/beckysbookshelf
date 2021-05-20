from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError


# Create your models here.
class Topics(models.Model):
    TopicID = models.IntegerField('TopicID', primary_key=True)
    Topic = models.CharField('Topic', max_length=200, null=True)
    DateAdded = models.DateTimeField('DateAdded', null=False, default=timezone.now)

    def __str__(self):
        return self.Topic

class Publishers(models.Model):
    PublisherID = models.IntegerField('PublisherID', primary_key=True)
    Publisher = models.CharField('Publisher', max_length=255, null=True)

    def __str__(self):
        return self.Publisher

class Series(models.Model):
    SeriesID = models.IntegerField('SeriesID', primary_key=True)
    Series = models.CharField('Series', max_length=255, null=True)
    DateAdded = models.DateTimeField('DateAdded', null=True, default=timezone.now)

    def __str__(self):
        return self.Series

class Conditions(models.Model):
    ConditionID = models.IntegerField('ConditionID', primary_key=True)
    Condition = models.CharField('Condition', max_length=255, null=True)

    def __str__(self):
        return self.Condition

class CoverType(models.Model):
    CoverID = models.IntegerField('CoverID', primary_key=True)
    Cover = models.CharField('Cover', max_length=255, null=True)
    def __str__(self):
        return self.Cover

class SmallShelfSigns(models.Model):
    SignID = models.IntegerField('SignID', primary_key=True)
    Description = models.CharField('Description', max_length=255, null=True)

    def __str__(self):
        return self.Description

class Customers(models.Model):
    CustomerID = models.IntegerField(primary_key=True)
    FirstName = models.CharField(max_length=255, null=True)
    LastName = models.CharField(max_length=255, null=False)
    Address = models.CharField(max_length=255, null=True)
    City = models.CharField(max_length=255, null=True)
    State = models.CharField(max_length=255, null=True)
    Zip = models.CharField(max_length=5, null=True)
    HomePhone = models.CharField(max_length=11, null=True)
    DateAdded = models.DateField(null=True, default=timezone.now)
    Email = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.LastName + ", " + self.FirstName

class Authors(models.Model):
    AuthorID = models.IntegerField('AuthorID', primary_key=True, db_column='AuthorID')
    FirstName = models.CharField(max_length=255, null=True)
    LastName = models.CharField(max_length=255, null=False)
    PrimaryTopic = models.ForeignKey(to=Topics,on_delete=models.CASCADE, db_column='PrimaryTopic', db_constraint=False)
    # DateAdded = models.DateField(null=True, default=timezone.now)

    def __str__(self):
        return self.FirstName + " " + self.LastName
    def get_absolute_url(self):
        return reverse('browse')

class Books(models.Model):
    BookID = models.IntegerField('BookID', primary_key=True, db_column='BookID')
    Title = models.CharField('Title', max_length=255, null=True)
    CopyrightYear = models.CharField('CopyrightYear', max_length=255, null=True)
    PublisherID = models.ForeignKey(to=Publishers, on_delete=models.CASCADE, db_column='PublisherID', db_constraint=False)
    SeriesID = models.ForeignKey(to=Series, on_delete=models.CASCADE, db_column='SeriesID', db_constraint=False)
    AuthorID = models.ForeignKey(to=Authors, on_delete=models.CASCADE, db_column='AuthorID', db_constraint=False)
    TopicID = models.ForeignKey(to=Topics, on_delete=models.CASCADE, db_column='TopicID', db_constraint=False)
    DateAdded = models.DateField('DateAdded', null=True, default=timezone.now)
    ISBN = models.CharField('ISBN', max_length=255, null=True)
        
    def __str__(self):
        return self.Title

    def get_absolute_url(self):
        return reverse('browse')

class Transactions(models.Model):
    ID = models.IntegerField(primary_key=True)
    BookID = models.ForeignKey(to=Books, on_delete=models.CASCADE, db_column='BookID', db_constraint=False)
    Price = models.FloatField(null=True)
    Resale = models.FloatField(null=True)
    TradePrice = models.FloatField(null=True)
    Qty = models.IntegerField(null=True)
    TradeAllowed = models.IntegerField(null=True)
    # PercentTrade = models.FloatField(null=True)
    CoverPrice = models.FloatField(null=True)
    Discount = models.IntegerField(null=True)
    NonTradex = models.FloatField('Non-Trade_x', null=True)
    CoverID = models.ForeignKey(to=CoverType, on_delete=models.CASCADE, db_column='CoverID', db_constraint=False)
    LastUpdate = models.DateField(null=True, default=timezone.now)
    NoTradeAllowed = models.IntegerField(null=True)
    TaxExempt = models.IntegerField(null=True)
    ConditionID = models.ForeignKey(to=Conditions, on_delete=models.CASCADE, db_column='ConditionID', db_constraint=False)
    DateOfSale = models.DateField(null=True, default=timezone.now)
    CustomerID = models.ForeignKey(to=Customers, on_delete=models.CASCADE, db_column='CustomerID', db_constraint=False)
    # Tax = models.FloatField(null=True)
    Cash = models.FloatField(null=True)
    Check = models.FloatField(null=True)
    CheckNum = models.FloatField(null=True)
    GiftCert = models.FloatField(null=True)
    Description = models.CharField(max_length=255, null=True)
    TaxRate = models.FloatField(null=True)
    SalesPerson = models.CharField(max_length=255, null=True)
    Type = models.CharField(max_length=255, null=True)
    TradeCost = models.FloatField(null=True)
    InOut = models.FloatField('In/Out', null=True)
    NonTradeY = models.FloatField('Non-Trade_Y', null=True)
    Labels = models.IntegerField("labels", null=True)
    def __str__(self):
        return str(self.Description)
