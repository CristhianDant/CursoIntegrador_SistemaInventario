import { useState, useEffect } from "react";
import { Bell, Database, Shield, User, AlertCircle, CheckCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";
import { Alert, AlertTitle } from "./ui/alert";
import { API_BASE_URL } from "../constants";

interface CompanyData {
  id_empresa: number;
  nombre_empresa: string;
  ruc: string;
  email: string;
  telefono: string;
  direccion: string;
  estado: boolean;
  fecha_registro: string;
}

export function SettingsManager() {
  // Estado para datos de empresa desde API
  const [company, setCompany] = useState<CompanyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Estado para configuraciones locales
  const [settings, setSettings] = useState({
    // Configuración de alertas
    lowStockThreshold: 20,
    expiryWarningDays: 7,
    emailNotifications: true,
    smsNotifications: false,
    autoRefresh: true,
    
    // Configuración del sistema
    currency: "USD",
    language: "es",
    timezone: "America/Mexico_City",
    dateFormat: "DD/MM/YYYY",
    backupFrequency: "daily"
  });

  // Cargar datos de empresa al montar
  useEffect(() => {
    fetchCompanyData();
  }, []);

  const fetchCompanyData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/v1/empresa/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Error al cargar configuración de empresa');
      }

      const data = await response.json();
      
      // La respuesta tiene formato { success: true, data: [...] }
      if (data.success && Array.isArray(data.data) && data.data.length > 0) {
        setCompany(data.data[0]); // Tomar la primera empresa
      }
    } catch (error) {
      console.error('Error cargando empresa:', error);
      setMessage({ type: 'error', text: 'Error al cargar la configuración de empresa' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCompany = async () => {
    if (!company) return;

    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/v1/empresa/${company.id_empresa}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre_empresa: company.nombre_empresa,
          ruc: company.ruc,
          email: company.email,
          telefono: company.telefono,
          direccion: company.direccion,
          estado: company.estado
        }),
      });

      if (!response.ok) {
        throw new Error('Error al guardar configuración');
      }

      const data = await response.json();
      
      if (data.success) {
        setMessage({ type: 'success', text: 'Configuración de empresa guardada correctamente' });
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (error) {
      console.error('Error guardando empresa:', error);
      setMessage({ type: 'error', text: 'Error al guardar la configuración' });
    } finally {
      setSaving(false);
    }
  };

  const handleCompanyChange = (field: keyof CompanyData, value: any) => {
    if (company) {
      setCompany({
        ...company,
        [field]: value
      });
    }
  };

  const handleSettingsChange = (field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Configuración</h2>
          <p className="text-muted-foreground">Personaliza el sistema según tus necesidades</p>
        </div>
      </div>

      {/* Messages */}
      {message && (
        <Alert className={message.type === 'success' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}>
          {message.type === 'success' ? 
            <CheckCircle className="h-4 w-4 text-green-600" /> : 
            <AlertCircle className="h-4 w-4 text-red-600" />
          }
          <AlertTitle className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
            {message.text}
          </AlertTitle>
        </Alert>
      )}

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <p className="text-muted-foreground">Cargando configuración...</p>
          </div>
        </div>
      )}

      {/* Tabs de configuración */}
      {!loading && (
        <Tabs defaultValue="company" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="company">
              <User className="h-4 w-4 mr-2" />
              Empresa
            </TabsTrigger>
            <TabsTrigger value="alerts">
              <Bell className="h-4 w-4 mr-2" />
              Alertas
            </TabsTrigger>
            <TabsTrigger value="system">
              <Database className="h-4 w-4 mr-2" />
              Sistema
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="h-4 w-4 mr-2" />
              Seguridad
            </TabsTrigger>
          </TabsList>

          {/* Configuración de Empresa */}
          <TabsContent value="company" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Información de la Empresa</CardTitle>
                <CardDescription>
                  Datos de tu pastelería para reportes y documentos
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {company && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="companyName">Nombre de la Empresa</Label>
                        <Input
                          id="companyName"
                          value={company.nombre_empresa}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                            handleCompanyChange('nombre_empresa', e.target.value)
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="ruc">RUC</Label>
                        <Input
                          id="ruc"
                          value={company.ruc}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                            handleCompanyChange('ruc', e.target.value)
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="contactEmail">Email de Contacto</Label>
                        <Input
                          id="contactEmail"
                          type="email"
                          value={company.email}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                            handleCompanyChange('email', e.target.value)
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="phone">Teléfono</Label>
                        <Input
                          id="phone"
                          value={company.telefono}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                            handleCompanyChange('telefono', e.target.value)
                          }
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="address">Dirección</Label>
                      <Textarea
                        id="address"
                        value={company.direccion}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => 
                          handleCompanyChange('direccion', e.target.value)
                        }
                        placeholder="Dirección completa de la pastelería"
                      />
                    </div>

                    <Separator />

                    <Button 
                      onClick={handleSaveCompany} 
                      disabled={saving}
                      className="w-full"
                    >
                      {saving ? 'Guardando...' : 'Guardar Cambios'}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración de Alertas */}
          <TabsContent value="alerts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Configuración de Alertas</CardTitle>
                <CardDescription>
                  Define cuando y cómo recibir notificaciones
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="lowStock">Umbral de Stock Bajo (%)</Label>
                    <Input
                      id="lowStock"
                      type="number"
                      value={settings.lowStockThreshold}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                        handleSettingsChange('lowStockThreshold', parseInt(e.target.value))
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Alerta cuando el stock esté por debajo de este porcentaje
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="expiryWarning">Días de Aviso de Vencimiento</Label>
                    <Input
                      id="expiryWarning"
                      type="number"
                      value={settings.expiryWarningDays}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                        handleSettingsChange('expiryWarningDays', parseInt(e.target.value))
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Días antes del vencimiento para mostrar alerta
                    </p>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Métodos de Notificación</h4>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Notificaciones por Email</Label>
                      <p className="text-xs text-muted-foreground">
                        Recibir alertas en tu correo electrónico
                      </p>
                    </div>
                    <Switch
                      checked={settings.emailNotifications}
                      onCheckedChange={(checked: boolean) => 
                        handleSettingsChange('emailNotifications', checked)
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Notificaciones SMS</Label>
                      <p className="text-xs text-muted-foreground">
                        Recibir alertas por mensaje de texto
                      </p>
                    </div>
                    <Switch
                      checked={settings.smsNotifications}
                      onCheckedChange={(checked: boolean) => 
                        handleSettingsChange('smsNotifications', checked)
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Actualización Automática</Label>
                      <p className="text-xs text-muted-foreground">
                        Actualizar alertas automáticamente
                      </p>
                    </div>
                    <Switch
                      checked={settings.autoRefresh}
                      onCheckedChange={(checked: boolean) => 
                        handleSettingsChange('autoRefresh', checked)
                      }
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración del Sistema */}
          <TabsContent value="system" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Preferencias del Sistema</CardTitle>
                <CardDescription>
                  Configuración regional y de respaldos
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="language">Idioma</Label>
                    <Select 
                      value={settings.language} 
                      onValueChange={(value: string) => handleSettingsChange('language', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="es">Español</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="pt">Português</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Zona Horaria</Label>
                    <Select 
                      value={settings.timezone} 
                      onValueChange={(value: string) => handleSettingsChange('timezone', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="America/Mexico_City">México (Ciudad de México)</SelectItem>
                        <SelectItem value="America/Bogota">Colombia (Bogotá)</SelectItem>
                        <SelectItem value="America/Lima">Perú (Lima)</SelectItem>
                        <SelectItem value="America/Buenos_Aires">Argentina (Buenos Aires)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dateFormat">Formato de Fecha</Label>
                    <Select 
                      value={settings.dateFormat} 
                      onValueChange={(value: string) => handleSettingsChange('dateFormat', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                        <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                        <SelectItem value="YYYY/MM/DD">YYYY/MM/DD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="currency">Moneda</Label>
                    <Select 
                      value={settings.currency} 
                      onValueChange={(value: string) => handleSettingsChange('currency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">Dólar (USD)</SelectItem>
                        <SelectItem value="MXN">Peso Mexicano (MXN)</SelectItem>
                        <SelectItem value="EUR">Euro (EUR)</SelectItem>
                        <SelectItem value="ARS">Peso Argentino (ARS)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Respaldos</h4>
                  <div className="space-y-2">
                    <Label htmlFor="backup">Frecuencia de Respaldo</Label>
                    <Select 
                      value={settings.backupFrequency} 
                      onValueChange={(value: string) => handleSettingsChange('backupFrequency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Cada hora</SelectItem>
                        <SelectItem value="daily">Diariamente</SelectItem>
                        <SelectItem value="weekly">Semanalmente</SelectItem>
                        <SelectItem value="monthly">Mensualmente</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button variant="outline" className="w-full">
                    Realizar Respaldo Ahora
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración de Seguridad */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Seguridad</CardTitle>
                <CardDescription>
                  Opciones de seguridad y privacidad de cuenta
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Gestión de Contraseña</h4>
                  <Button variant="outline" className="w-full">
                    Cambiar Contraseña
                  </Button>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Sesiones Activas</h4>
                  <div className="space-y-2 text-sm">
                    <p className="text-muted-foreground">
                      Gestiona tus sesiones activas
                    </p>
                  </div>
                  <Button variant="outline" className="w-full text-red-600">
                    Cerrar Todas las Sesiones
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
