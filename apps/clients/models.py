from django.db import models

# Create your models here.
class Client(models.Model):

    """
    Tabla: clients
    Clientes del negocio.
    
    Nota importante: el teléfono es único porque es el identificador
    principal del cliente. Si alguien agenda dos veces con el mismo
    teléfono, se reutiliza el mismo registro de cliente.
    """

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas internas, solo visible para admin'
    ) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


