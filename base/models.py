from django.db import models

class Department(models.Model):
    Name = models.CharField(max_length=255)
    Description = models.TextField(blank=True)  # A longer field suitable for detailed descriptions
    Location = models.CharField(max_length=255, blank=True)  # Optional field for location

    def __str__(self):
        return self.Name

class PositionLevel(models.Model):
    LevelName = models.CharField(max_length=255)

    def __str__(self):
        return self.LevelName

class Position(models.Model):
    Name = models.CharField(max_length=255)
    Department = models.ForeignKey(Department, on_delete=models.PROTECT)
    Level = models.ForeignKey(PositionLevel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.Name} in {self.Department.Name} - {self.Level.LevelName}"
# Gender choices
GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

# Marital status choices
MARITAL_STATUS_CHOICES = (
    ('Single', 'Single'),
    ('Married', 'Married'),

    # add other statuses as required
)

class Employee(models.Model):
    EmployeeID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255)
    MiddleName = models.CharField(max_length=255, blank=True, null=True)  # Optional field
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    DateHired = models.DateField(null=True, blank=True)  # Made it optional
    DateOfBirth = models.DateField()
    Nationality = models.CharField(max_length=255)  
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    MaritalStatus = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    Email = models.EmailField(unique=True)
    Phone = models.CharField(max_length=15, unique=True)  # Optional field
    InsuranceNumber = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Optional field
    PassportNumber = models.CharField(max_length=255, unique=True)
    ProfileImage = models.ImageField(upload_to='employee_images/', blank=True, null=True)  # Made it optional
    Address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)  # Made it optional

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

class Signature(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    signature_file = models.ImageField(upload_to='signatures/')


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='employee_documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.employee.FirstName} uploaded on {self.uploaded_at}"

class Address(models.Model):
    Employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)  # One-to-One relationship
    AddressDescription = models.TextField(blank=True)  # A description field for the address, optional
    Street = models.TextField()
    City = models.CharField(max_length=255)
    State = models.CharField(max_length=255)
    Country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Street}, {self.City}, {self.State}, {self.Country}"


class Dependent(models.Model):
    DependentID = models.AutoField(primary_key=True)
    Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    DependentName = models.CharField(max_length=255, null=True, blank=True)
    RELATIONSHIP_CHOICES = (
        ('Spouse', 'Spouse'),
        ('Child', 'Child'),
        ('Parent', 'Parent'),
        # Add other relationships as needed
    )
    Relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    DateOfBirth = models.DateField()

    def __str__(self):
        return f"{self.DependentName} - {self.Relationship} of {self.Employee.FirstName} {self.Employee.LastName}"
    



