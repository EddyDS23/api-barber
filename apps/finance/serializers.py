# apps/finance/serializers.py

from rest_framework import serializers
from .models import FinancialTransaction, TypeTransaction, CategoryTransaction


# ─────────────────────────────────────────────────────────────
#  Tipos de transacción (Ingreso / Egreso)
# ─────────────────────────────────────────────────────────────

class TypeTransactionSerializer(serializers.ModelSerializer):
    """CRUD completo para tipos de transacción."""
    class Meta:
        model  = TypeTransaction
        fields = ['id', 'name']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido.")
        qs = TypeTransaction.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un tipo con ese nombre.")
        return value.strip()


# ─────────────────────────────────────────────────────────────
#  Categorías de transacción
# ─────────────────────────────────────────────────────────────

class CategoryTransactionSerializer(serializers.ModelSerializer):
    """CRUD completo para categorías de transacción."""
    class Meta:
        model  = CategoryTransaction
        fields = ['id', 'name']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido.")
        qs = CategoryTransaction.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una categoría con ese nombre.")
        return value.strip()


# ─────────────────────────────────────────────────────────────
#  Transacción financiera (CRUD completo)
# ─────────────────────────────────────────────────────────────

class FinancialTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer principal para crear, editar y listar transacciones.

    Patrón doble campo:
      - type / category           → escritura (recibe ID)
      - type_name / category_name → lectura (retorna nombre legible)

    Sobre el campo amount:
      El schema de la DB dice:
        'Positivo para ingresos, negativo para egresos'
      Constraint en DB: CHECK (amount != 0)
      → Solo prohibimos el 0, los negativos son válidos (egresos).
    """

    type_name     = serializers.CharField(source='type.name',     read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    type          = serializers.PrimaryKeyRelatedField(queryset=TypeTransaction.objects.all())
    category      = serializers.PrimaryKeyRelatedField(queryset=CategoryTransaction.objects.all())

    class Meta:
        model  = FinancialTransaction
        fields = [
            'id',
            'type',
            'type_name',
            'category',
            'category_name',
            'concept',
            'amount',
            'date',
            'notes',
            'appointment',
        ]

    def validate_concept(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El concepto es requerido.")
        if len(value) > 200:
            raise serializers.ValidationError("El concepto no puede exceder 200 caracteres.")
        return value.strip()

    def validate_amount(self, value):
        """
        DB constraint: CHECK (amount != 0)
        Positivo = ingreso | Negativo = egreso
        Solo prohibimos el 0 y más de 2 decimales.
        """
        if value == 0:
            raise serializers.ValidationError("El monto no puede ser 0.")

        # abs() para validar decimales tanto en positivos como negativos
        str_value = str(abs(value))
        if '.' in str_value:
            if len(str_value.split('.')[1]) > 2:
                raise serializers.ValidationError("El monto solo puede tener hasta 2 decimales.")

        return value

    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("La fecha es requerida.")
        return value