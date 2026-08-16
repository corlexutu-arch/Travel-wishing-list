from django.db import models

# Create your models here.

class DestinatieVacanta(models.Model):
    
    OPTIUNI_CATEGORIE = [
        ('Natura', 'Natura'),
        ('Urban', 'Urban'),
        ('Mixed', 'Mixed'),
    ]

    link_original = models.URLField(max_length=500)
    tara = models.CharField(max_length=100)
    locul = models.CharField(max_length=255)
    categorie = models.CharField(max_length=50, choices=OPTIUNI_CATEGORIE)
    tip_activitate = models.TextField() # unde se salveaza cuvintele cheie
    data_adaugarii = models.DateTimeField(auto_now_add=True) # punere automată a datei curente

    def __str__(self):
        return f"{self.locul} ({self.tara})"