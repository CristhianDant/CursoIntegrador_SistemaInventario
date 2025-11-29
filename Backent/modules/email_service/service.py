import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List, Tuple
from datetime import datetime
from loguru import logger

from config import settings
from .model import ColaEmail
from .schemas import EmailCreate, CredencialesEmailData
from modules.empresa.model import Empresa


class EmailService:
    """
    Servicio de email con soporte para cola offline usando Gmail SMTP.
    Si el envío falla (sin internet), el email se encola en la base de datos.
    El remitente se obtiene dinámicamente de la configuración SMTP.
    """
    
    MAX_INTENTOS = 3
    
    def _is_configured(self) -> bool:
        """Verifica si Gmail SMTP está configurado"""
        return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
    
    def _get_email_from(self, db: Session) -> Tuple[str, str]:
        """
        Obtiene el nombre de la empresa para mostrar y el email SMTP.
        Retorna (nombre_para_mostrar, email_smtp)
        """
        try:
            empresa = db.query(Empresa).filter(Empresa.estado == True).first()
            nombre = empresa.nombre_empresa if empresa and empresa.nombre_empresa else "Sistema de Inventario"
            return nombre, settings.SMTP_USER
        except Exception as e:
            logger.warning(f"No se pudo obtener nombre de empresa: {e}")
            return "Sistema de Inventario", settings.SMTP_USER
    
    def _enviar_email_smtp(self, db: Session, destinatario: str, asunto: str, cuerpo_html: str) -> Tuple[bool, Optional[str]]:
        """
        Intenta enviar un email usando Gmail SMTP.
        Retorna (éxito, mensaje_error)
        """
        if not self._is_configured():
            return False, "SMTP no configurado. Configura SMTP_USER y SMTP_PASSWORD en config.py"
        
        try:
            nombre_empresa, email_from = self._get_email_from(db)
            
            # Crear mensaje
            mensaje = MIMEMultipart('alternative')
            mensaje['Subject'] = asunto
            mensaje['From'] = f"{nombre_empresa} <{email_from}>"
            mensaje['To'] = destinatario
            
            # Agregar contenido HTML
            parte_html = MIMEText(cuerpo_html, 'html', 'utf-8')
            mensaje.attach(parte_html)
            
            # Conectar y enviar
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as servidor:
                servidor.starttls()  # Habilitar TLS
                servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                servidor.sendmail(email_from, destinatario, mensaje.as_string())
            
            logger.info(f"Email enviado exitosamente a {destinatario} desde {email_from}")
            return True, None
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Error de autenticación SMTP. Verifica tu email y contraseña de aplicación."
            logger.error(f"{error_msg}: {e}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            logger.error(f"Error al enviar email a {destinatario}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error al enviar email a {destinatario}: {error_msg}")
            return False, error_msg
    
    def enviar_o_encolar(self, db: Session, email_data: EmailCreate) -> Tuple[bool, str]:
        """
        Intenta enviar el email. Si falla, lo encola en la base de datos.
        Retorna (enviado_inmediatamente, mensaje)
        """
        # Intentar enviar directamente
        exito, error = self._enviar_email_smtp(
            db,
            email_data.destinatario,
            email_data.asunto,
            email_data.cuerpo_html
        )
        
        if exito:
            # Guardar registro como ENVIADO para historial
            email_record = ColaEmail(
                destinatario=email_data.destinatario,
                asunto=email_data.asunto,
                cuerpo_html=email_data.cuerpo_html,
                estado='ENVIADO',
                intentos=1,
                fecha_envio=datetime.now()
            )
            db.add(email_record)
            db.commit()
            return True, "Email enviado correctamente"
        
        # Si falló, encolar
        email_record = ColaEmail(
            destinatario=email_data.destinatario,
            asunto=email_data.asunto,
            cuerpo_html=email_data.cuerpo_html,
            estado='PENDIENTE',
            intentos=1,
            ultimo_error=error
        )
        db.add(email_record)
        db.commit()
        
        return False, f"Email encolado para envío posterior. Error: {error}"
    
    def procesar_cola(self, db: Session) -> dict:
        """
        Procesa todos los emails pendientes en la cola.
        Retorna estadísticas del procesamiento.
        """
        pendientes = db.query(ColaEmail).filter(
            ColaEmail.estado == 'PENDIENTE',
            ColaEmail.intentos < self.MAX_INTENTOS
        ).all()
        
        resultados = {
            'procesados': 0,
            'enviados': 0,
            'fallidos': 0,
            'detalles': []
        }
        
        for email in pendientes:
            resultados['procesados'] += 1
            
            exito, error = self._enviar_email_smtp(
                db,
                email.destinatario,
                email.asunto,
                email.cuerpo_html
            )
            
            email.intentos += 1
            
            if exito:
                email.estado = 'ENVIADO'
                email.fecha_envio = datetime.now()
                resultados['enviados'] += 1
                resultados['detalles'].append({
                    'id': email.id_email,
                    'destinatario': email.destinatario,
                    'resultado': 'ENVIADO'
                })
            else:
                email.ultimo_error = error
                if email.intentos >= self.MAX_INTENTOS:
                    email.estado = 'ERROR'
                resultados['fallidos'] += 1
                resultados['detalles'].append({
                    'id': email.id_email,
                    'destinatario': email.destinatario,
                    'resultado': 'FALLIDO',
                    'error': error
                })
        
        db.commit()
        return resultados
    
    def get_estadisticas(self, db: Session) -> dict:
        """Obtiene estadísticas de la cola de emails"""
        pendientes = db.query(ColaEmail).filter(ColaEmail.estado == 'PENDIENTE').count()
        enviados = db.query(ColaEmail).filter(ColaEmail.estado == 'ENVIADO').count()
        errores = db.query(ColaEmail).filter(ColaEmail.estado == 'ERROR').count()
        
        return {
            'pendientes': pendientes,
            'enviados': enviados,
            'errores': errores,
            'total': pendientes + enviados + errores
        }
    
    def get_pendientes(self, db: Session) -> List[ColaEmail]:
        """Obtiene lista de emails pendientes"""
        return db.query(ColaEmail).filter(ColaEmail.estado == 'PENDIENTE').all()
    
    def limpiar_emails_antiguos(self, db: Session, dias: int = 1) -> int:
        """
        Elimina emails enviados o con error que tengan más de X días.
        Retorna la cantidad de registros eliminados.
        """
        from datetime import timedelta
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        # Eliminar emails ENVIADOS o ERROR con más de X días
        eliminados = db.query(ColaEmail).filter(
            ColaEmail.estado.in_(['ENVIADO', 'ERROR']),
            ColaEmail.fecha_creacion < fecha_limite
        ).delete(synchronize_session=False)
        
        db.commit()
        return eliminados
    
    # ========== Templates de Email ==========
    
    def _get_nombre_empresa(self, db: Session) -> str:
        """Obtiene el nombre de la empresa activa"""
        try:
            empresa = db.query(Empresa).filter(Empresa.estado == True).first()
            if empresa and empresa.nombre_empresa:
                return empresa.nombre_empresa
            return "La Empresa"
        except Exception:
            return "La Empresa"
    
    def generar_email_credenciales(self, db: Session, datos: CredencialesEmailData) -> EmailCreate:
        """
        Genera el email de bienvenida con credenciales para un nuevo usuario.
        """
        nombre_empresa = self._get_nombre_empresa(db)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .credentials {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .credential-item {{ margin: 10px 0; }}
                .credential-label {{ font-weight: bold; color: #555; }}
                .credential-value {{ font-family: monospace; background: #f0f0f0; padding: 8px 12px; border-radius: 4px; display: inline-block; margin-top: 5px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍰 Bienvenido Trabajador</h1>
                    <p>Comenzaremos con un nuevo capítulo juntos.</p>
                </div>
                <div class="content">
                    <h2>¡Hola {datos.nombre_completo}!</h2>
                    <p>Se ha creado tu cuenta en el sistema. A continuación encontrarás tus credenciales de acceso:</p>
                    
                    <div class="credentials">
                        <div class="credential-item">
                            <div class="credential-label">📧 Correo electrónico:</div>
                            <div class="credential-value">{datos.email}</div>
                        </div>
                        <div class="credential-item">
                            <div class="credential-label">🔑 Contraseña:</div>
                            <div class="credential-value">{datos.password}</div>
                        </div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Por seguridad, te recomendamos cambiar tu contraseña después del primer inicio de sesión.</li>
                            <li>No compartas tus credenciales con nadie.</li>
                            <li>Si no solicitaste esta cuenta, contacta al administrador del sistema.</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>© {datetime.now().year} {nombre_empresa} - Sistema de Inventario</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailCreate(
            destinatario=datos.email,
            asunto=f"🍰 Bienvenido a {nombre_empresa} - Tus credenciales de acceso",
            cuerpo_html=html_content
        )
    
    def enviar_credenciales_usuario(self, db: Session, datos: CredencialesEmailData) -> Tuple[bool, str]:
        """
        Envía (o encola) el email de credenciales para un nuevo usuario.
        """
        email_data = self.generar_email_credenciales(db, datos)
        return self.enviar_o_encolar(db, email_data)
