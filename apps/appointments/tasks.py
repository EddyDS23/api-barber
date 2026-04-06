import resend
from celery import shared_task
from django.conf import settings

def _build_email_html(data: dict) -> str:
    """
    Construye el HTML del correo de confirmación.
    data keys: booking_id, client_name, services, barber,
               date, time, total_amount, maps_url,
               cancellation_hours, business_name
    """
    services_list = ''.join(
        f'<li style="margin:4px 0;">{s}</li>' for s in data['services']
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="margin:0;padding:0;background:#f4f4f5;font-family:'Segoe UI',Arial,sans-serif;">

      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#f4f4f5;padding:32px 0;">
        <tr>
          <td align="center">

            <!-- Card principal -->
            <table width="580" cellpadding="0" cellspacing="0"
                   style="background:#ffffff;border-radius:12px;
                          overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">

              <!-- Header -->
              <tr>
                <td style="background:#18181b;padding:32px 40px;text-align:center;">
                  <p style="margin:0;color:#a1a1aa;font-size:13px;
                             letter-spacing:2px;text-transform:uppercase;">
                    {data['business_name']}
                  </p>
                  <h1 style="margin:8px 0 0;color:#ffffff;font-size:26px;
                              font-weight:700;">
                    ¡Reserva Confirmada!
                  </h1>
                </td>
              </tr>

              <!-- ID de reserva -->
              <tr>
                <td style="background:#fafafa;padding:16px 40px;
                            border-bottom:1px solid #e4e4e7;text-align:center;">
                  <span style="font-size:13px;color:#71717a;">
                    ID de Reserva
                  </span>
                  <br/>
                  <span style="font-size:22px;font-weight:800;
                                color:#18181b;letter-spacing:1px;">
                    #{data['booking_id']}
                  </span>
                </td>
              </tr>

              <!-- Cuerpo -->
              <tr>
                <td style="padding:32px 40px;">

                  <p style="margin:0 0 4px;color:#71717a;font-size:13px;">
                    Hola <strong style="color:#18181b;">
                      {data['client_name']}
                    </strong>, tu cita está confirmada:
                  </p>

                  <!-- Resumen -->
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="margin:24px 0;border:1px solid #e4e4e7;
                                border-radius:8px;overflow:hidden;">

                    <tr style="background:#fafafa;">
                      <td style="padding:12px 16px;font-size:13px;
                                  color:#71717a;width:40%;">
                        Servicio(s)
                      </td>
                      <td style="padding:12px 16px;font-size:14px;
                                  font-weight:600;color:#18181b;">
                        <ul style="margin:0;padding-left:16px;">
                          {services_list}
                        </ul>
                      </td>
                    </tr>

                    <tr>
                      <td style="padding:12px 16px;font-size:13px;
                                  color:#71717a;border-top:1px solid #e4e4e7;">
                        Barbero
                      </td>
                      <td style="padding:12px 16px;font-size:14px;
                                  font-weight:600;color:#18181b;
                                  border-top:1px solid #e4e4e7;">
                        {data['barber']}
                      </td>
                    </tr>

                    <tr style="background:#fafafa;">
                      <td style="padding:12px 16px;font-size:13px;
                                  color:#71717a;border-top:1px solid #e4e4e7;">
                        Fecha
                      </td>
                      <td style="padding:12px 16px;font-size:14px;
                                  font-weight:600;color:#18181b;
                                  border-top:1px solid #e4e4e7;">
                        {data['date']}
                      </td>
                    </tr>

                    <tr>
                      <td style="padding:12px 16px;font-size:13px;
                                  color:#71717a;border-top:1px solid #e4e4e7;">
                        Hora
                      </td>
                      <td style="padding:12px 16px;font-size:14px;
                                  font-weight:600;color:#18181b;
                                  border-top:1px solid #e4e4e7;">
                        {data['time']}
                      </td>
                    </tr>

                    <tr style="background:#fafafa;">
                      <td style="padding:12px 16px;font-size:13px;
                                  color:#71717a;border-top:1px solid #e4e4e7;">
                        Total
                      </td>
                      <td style="padding:12px 16px;font-size:16px;
                                  font-weight:800;color:#18181b;
                                  border-top:1px solid #e4e4e7;">
                        ${data['total_amount']}
                      </td>
                    </tr>

                  </table>

                  <!-- Ubicación -->
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="margin:0 0 24px;">
                    <tr>
                      <td style="background:#f0fdf4;border:1px solid #bbf7d0;
                                  border-radius:8px;padding:16px;">
                        <p style="margin:0 0 8px;font-size:13px;
                                   font-weight:700;color:#166534;">
                          📍 Ubicación
                        </p>
                        <a href="{data['maps_url']}"
                           style="color:#16a34a;font-size:14px;
                                   text-decoration:none;font-weight:600;">
                          Ver en Google Maps →
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Políticas -->
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="background:#fff7ed;border:1px solid #fed7aa;
                                  border-radius:8px;padding:16px;">
                        <p style="margin:0 0 8px;font-size:13px;
                                   font-weight:700;color:#9a3412;">
                          📋 Recuerda
                        </p>
                        <ul style="margin:0;padding-left:18px;
                                   color:#9a3412;font-size:13px;
                                   line-height:1.7;">
                          <li>Llega <strong>10 minutos antes</strong>
                              de tu cita.</li>
                          <li>Cancelaciones con al menos
                              <strong>{data['cancellation_hours']} horas</strong>
                              de anticipación.</li>
                          <li>Guarda tu ID de reserva
                              <strong>#{data['booking_id']}</strong>
                              para cualquier consulta.</li>
                        </ul>
                      </td>
                    </tr>
                  </table>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#fafafa;padding:20px 40px;
                            border-top:1px solid #e4e4e7;text-align:center;">
                  <p style="margin:0;color:#a1a1aa;font-size:12px;">
                    Este correo fue enviado automáticamente por
                    {data['business_name']}.<br/>
                    Por favor no respondas a este mensaje.
                  </p>
                </td>
              </tr>

            </table>
            <!-- /Card -->

          </td>
        </tr>
      </table>

    </body>
    </html>
    """


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_confirmation_email(self, appointment_id: int):
    """
    Tarea Celery: envía correo de confirmación al cliente.
    Se reintenta hasta 3 veces si falla (ej. Resend caído).
    """
    from apps.appointments.models import Appointment
    from apps.core.models import BusinessSettings

    try:
        appt = (
            Appointment.objects
            .select_related('client', 'barber', 'status')
            .prefetch_related('appointmentservice_set__service')
            .get(pk=appointment_id)
        )
    except Appointment.DoesNotExist:
        return {'error': f'Appointment {appointment_id} not found'}

    # Solo enviar si tiene email
    if not appt.client.email:
        return {'skipped': 'No client email'}

    # Datos del negocio
    try:
        biz = BusinessSettings.objects.get(id=1)
        cancellation_hours = biz.cancellation_hours_before
        business_name = biz.business_name
    except BusinessSettings.DoesNotExist:
        cancellation_hours = 24
        business_name = settings.BUSINESS_NAME

    # Armar datos del correo
    services = [
        ap_srv.service.name
        for ap_srv in appt.appointmentservice_set.all()
    ]

    booking_id = f'BK-{appt.id:04d}'

    data = {
        'booking_id':          booking_id,
        'client_name':         appt.client.full_name,
        'services':            services,
        'barber':              appt.barber.name,
        'date':                appt.date.strftime('%d de %B de %Y'),
        'time':                appt.time.strftime('%H:%M'),
        'total_amount':        f'{appt.total_amount:.2f}',
        'maps_url':            settings.BUSINESS_MAPS_URL,
        'cancellation_hours':  cancellation_hours,
        'business_name':       business_name,
    }

    html_content = _build_email_html(data)

    try:
        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            'from':    settings.FROM_EMAIL,
            'to':      "carrilloedgar408@gmail.com",
            'subject': f'✂️ Reserva confirmada #{booking_id} — {business_name}',
            'html':    html_content,
        })

        return {'sent': True, 'to': appt.client.email, 'booking_id': booking_id}

    except Exception as exc:
        raise self.retry(exc=exc)