from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    maker_name = models.CharField(null=False, max_length=30, default='BMW')
    description = models.CharField(null=False, max_length=500)
    #dob = models.DateField(null=True)
    
    # Create a toString method for object string representation
    def __str__(self):
        return self.maker_name + " " + self.description


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    
    SUV = 'SUV'
    SEDAN = 'Sedan'
    WAGON = 'Wagon'
    COUPE = 'Coupe'
    TYPE_CHOICES = [
        (SUV, 'SUV'),
        (SEDAN, 'Sedan'),
        (WAGON, 'Wagon'),
        (COUPE, 'Coupe')]
    
    model_name = models.CharField(null=False, max_length=30, default='X7')
    dealer_ID = models.IntegerField(default=1)
    car_type = models.CharField(null=False,max_length=30, choices=TYPE_CHOICES, default=SEDAN)
    year = models.DateField(null=True)
    makers = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    
    # Create a toString method for object string representation
    def __str__(self):
        return self.model_name + " " + str(self.dealer_ID) + " " + self.car_type + " " + str(self.year)


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
