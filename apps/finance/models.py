from django.db import models

from apps.appointments.models import Appointment

# Create your models here.
class TypeTransaction(models.Model):
    """
    Tabla: type_transactions
    Catálogo de tipos: Ingreso, Egreso
    """

    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'type_transactions'
        verbose_name = 'Tipo de Transaccion'
        verbose_name_plural = 'Tipos de Transacciones'
    
    def __str__(self):
        return self.name
    

class CategoryTransaction(models.Model):
    """
    Tabla: category_transactions
    Categorías: Servicio, Propina, Producto, Salario, Renta, etc.
    """

    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category_transactions'
        verbose_name = 'Categoria de Transaccion'
        verbose_name_plural = 'Categorias de Transacciones'

    def __str__(self):
        return self.name
    

class FinancialTransaction(models.Model):
    """
    Tabla: financial_transactions
    Registro de todos los movimientos financieros del negocio.

    Puntos clave:
    - amount positivo → Ingreso
    - amount negativo → Egreso
    - appointment es opcional (null=True) porque no todos los
      ingresos/egresos están ligados a una cita. Ejemplo:
      pago de renta, compra de insumos, etc.
    """

    type = models.ForeignKey(
        TypeTransaction,
        on_delete=models.RESTRICT,
        db_column='type_id',
        related_name='transactions'
    )
    category = models.ForeignKey(
        CategoryTransaction,
        on_delete=models.RESTRICT,
        db_column='category_id',
        related_name='transactions'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='appointment_id',
        related_name='transactions'
    )
    concept = models.CharField(
        max_length=200,
        help_text='Descripcion breve del movimiento'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Positivo para ingresos, Negativo para egresos'
    )
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_transactions'
        verbose_name = 'Transacción Financiera'
        verbose_name_plural = 'Transacciones Financieras'
        ordering = ['-date', '-created_at']

    def __str__(self):
        tipo = 'Ingreso' if self.amount > 0 else 'Egreso'
        return f"{tipo} - {self.concept} (${abs(self.amount)})"

