import { useState, useEffect } from "react";
import { 
  AlertTriangle, 
  Calendar, 
  Package, 
  Bell, 
  CheckCircle, 
  X,
  Filter,
  RefreshCw,
  Loader2
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { API_BASE_URL } from "../constants";

// Interfaces basadas en los schemas del backend
interface NotificacionResponse {
  id_notificacion: number;
  tipo: 'STOCK_CRITICO' | 'VENCIMIENTO_PROXIMO' | 'USAR_HOY' | 'VENCIDO';
  titulo: string;
  mensaje: string;
  id_insumo?: number;
  semaforo?: 'VERDE' | 'AMARILLO' | 'ROJO';
  dias_restantes?: number;
  cantidad_afectada?: string;
  leida: boolean;
  activa: boolean;
  fecha_creacion: string;
  nombre_insumo?: string;
  codigo_insumo?: string;
}

interface InsumoSemaforo {
  id_insumo: number;
  codigo: string;
  nombre: string;
  unidad_medida: string;
  cantidad_disponible: number;
  fecha_vencimiento: string;
  dias_restantes: number;
  semaforo: 'VERDE' | 'AMARILLO' | 'ROJO';
  accion_sugerida: string;
  id_ingreso_detalle: number;
  numero_lote?: string;
}

interface ResumenSemaforo {
  fecha_consulta: string;
  total_verde: number;
  total_amarillo: number;
  total_rojo: number;
  total_vencidos: number;
  items_rojo: InsumoSemaforo[];
  items_amarillo: InsumoSemaforo[];
}

interface InsumoStockCritico {
  id_insumo: number;
  codigo: string;
  nombre: string;
  unidad_medida: string;
  stock_actual: number;
  stock_minimo: number;
  deficit: number;
  es_critico: boolean;
  porcentaje_stock: number;
}

interface ResumenStockCritico {
  fecha_consulta: string;
  total_sin_stock: number;
  total_bajo_minimo: number;
  total_normal: number;
  items: InsumoStockCritico[];
}

interface ResumenAlertas {
  fecha: string;
  total_no_leidas: number;
  por_tipo: Record<string, number>;
  ultima_ejecucion_job?: string;
}

export function AlertsManager() {
  const [notificaciones, setNotificaciones] = useState<NotificacionResponse[]>([]);
  const [semaforo, setSemaforo] = useState<ResumenSemaforo | null>(null);
  const [stockCritico, setStockCritico] = useState<ResumenStockCritico | null>(null);
  const [resumen, setResumen] = useState<ResumenAlertas | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedPriority, setSelectedPriority] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [showDismissed, setShowDismissed] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [notifRes, semaforoRes, stockRes, resumenRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/v1/alertas/notificaciones?limit=100`),
        fetch(`${API_BASE_URL}/v1/alertas/semaforo`),
        fetch(`${API_BASE_URL}/v1/alertas/stock-critico`),
        fetch(`${API_BASE_URL}/v1/alertas/resumen`)
      ]);

      if (notifRes.status === 'fulfilled' && notifRes.value.ok) {
        const data = await notifRes.value.json();
        setNotificaciones(data.data || data || []);
      }

      if (semaforoRes.status === 'fulfilled' && semaforoRes.value.ok) {
        const data = await semaforoRes.value.json();
        setSemaforo(data.data || data);
      }

      if (stockRes.status === 'fulfilled' && stockRes.value.ok) {
        const data = await stockRes.value.json();
        setStockCritico(data.data || data);
      }

      if (resumenRes.status === 'fulfilled' && resumenRes.value.ok) {
        const data = await resumenRes.value.json();
        setResumen(data.data || data);
      }

    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Error al cargar las alertas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto refresh cada 2 minutos si está activado
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchData, 2 * 60 * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const handleMarkAsRead = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/alertas/notificaciones/${id}/leida`, {
        method: 'PATCH'
      });
      if (response.ok) {
        setNotificaciones(prev => 
          prev.map(n => n.id_notificacion === id ? { ...n, leida: true } : n)
        );
      }
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/alertas/notificaciones/marcar-todas-leidas`, {
        method: 'PATCH'
      });
      if (response.ok) {
        setNotificaciones(prev => prev.map(n => ({ ...n, leida: true })));
        fetchData();
      }
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const filteredNotificaciones = notificaciones.filter(notif => {
    const matchesType = selectedType === "all" || notif.tipo === selectedType;
    const matchesPriority = selectedPriority === "all" || 
      (selectedPriority === "high" && (notif.semaforo === 'ROJO' || notif.tipo === 'VENCIDO')) ||
      (selectedPriority === "medium" && notif.semaforo === 'AMARILLO') ||
      (selectedPriority === "low" && notif.semaforo === 'VERDE');
    const matchesDismissed = showDismissed || !notif.leida;
    
    return matchesType && matchesPriority && matchesDismissed;
  });

  const getAlertIcon = (tipo: NotificacionResponse['tipo']) => {
    switch (tipo) {
      case 'VENCIDO':
        return <AlertTriangle className="h-4 w-4" />;
      case 'VENCIMIENTO_PROXIMO':
      case 'USAR_HOY':
        return <Calendar className="h-4 w-4" />;
      case 'STOCK_CRITICO':
        return <Package className="h-4 w-4" />;
    }
  };

  const getAlertColor = (tipo: NotificacionResponse['tipo'], semaforo?: string) => {
    if (tipo === 'VENCIDO') return 'border-red-200 bg-red-50';
    if (semaforo === 'ROJO' || tipo === 'USAR_HOY') return 'border-red-200 bg-red-50';
    if (semaforo === 'AMARILLO') return 'border-orange-200 bg-orange-50';
    if (tipo === 'STOCK_CRITICO') return 'border-orange-200 bg-orange-50';
    return 'border-yellow-200 bg-yellow-50';
  };

  const getPriorityBadge = (tipo: NotificacionResponse['tipo'], semaforo?: string) => {
    if (tipo === 'VENCIDO' || semaforo === 'ROJO') return 'destructive' as const;
    if (semaforo === 'AMARILLO' || tipo === 'STOCK_CRITICO') return 'secondary' as const;
    return 'outline' as const;
  };

  const stats = {
    total: notificaciones.filter(n => !n.leida).length,
    high: notificaciones.filter(n => !n.leida && (n.semaforo === 'ROJO' || n.tipo === 'VENCIDO')).length,
    reviewDate: notificaciones.filter(n => !n.leida && n.tipo === 'VENCIDO').length,
    expiring: notificaciones.filter(n => !n.leida && (n.tipo === 'VENCIMIENTO_PROXIMO' || n.tipo === 'USAR_HOY')).length,
    lowStock: notificaciones.filter(n => !n.leida && n.tipo === 'STOCK_CRITICO').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Cargando alertas...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Centro de Alertas</h2>
          <p className="text-muted-foreground">Monitoreo en tiempo real de tu inventario</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Switch 
            id="auto-refresh" 
            checked={autoRefresh}
            onCheckedChange={setAutoRefresh}
          />
          <Label htmlFor="auto-refresh" className="text-sm">
            Actualización automática
          </Label>
          <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-600">{error}</AlertDescription>
        </Alert>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Alertas</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Bell className="h-5 w-5 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Prioridad Alta</p>
                <p className="text-2xl font-bold text-red-600">{stats.high}</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Revisar Fecha</p>
                <p className="text-2xl font-bold text-red-600">{stats.reviewDate}</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Por Vencer</p>
                <p className="text-2xl font-bold text-orange-600">{stats.expiring}</p>
              </div>
              <Calendar className="h-5 w-5 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Stock Bajo</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.lowStock}</p>
              </div>
              <Package className="h-5 w-5 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-4 gap-4">
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue placeholder="Tipo de alerta" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  <SelectItem value="VENCIDO">Vencidos</SelectItem>
                  <SelectItem value="USAR_HOY">Usar hoy</SelectItem>
                  <SelectItem value="VENCIMIENTO_PROXIMO">Por vencer</SelectItem>
                  <SelectItem value="STOCK_CRITICO">Stock bajo</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedPriority} onValueChange={setSelectedPriority}>
                <SelectTrigger>
                  <SelectValue placeholder="Prioridad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las prioridades</SelectItem>
                  <SelectItem value="high">Alta (Rojo)</SelectItem>
                  <SelectItem value="medium">Media (Amarillo)</SelectItem>
                  <SelectItem value="low">Baja (Verde)</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center space-x-2">
                <Switch 
                  id="show-dismissed" 
                  checked={showDismissed}
                  onCheckedChange={setShowDismissed}
                />
                <Label htmlFor="show-dismissed" className="text-sm">
                  Mostrar leídas
                </Label>
              </div>

              <Button variant="outline" size="sm" onClick={handleMarkAllAsRead}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Marcar todas como leídas
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Alertas */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">Todas ({filteredNotificaciones.length})</TabsTrigger>
          <TabsTrigger value="high">
            Alta ({filteredNotificaciones.filter(n => n.semaforo === 'ROJO' || n.tipo === 'VENCIDO').length})
          </TabsTrigger>
          <TabsTrigger value="expiring">
            Por Vencer ({filteredNotificaciones.filter(n => n.tipo === 'VENCIMIENTO_PROXIMO' || n.tipo === 'USAR_HOY').length})
          </TabsTrigger>
          <TabsTrigger value="stock">
            Stock ({filteredNotificaciones.filter(n => n.tipo === 'STOCK_CRITICO').length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {filteredNotificaciones.length === 0 ? (
            <Card>
              <CardContent className="pt-8 text-center">
                <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">¡Todo bajo control!</h3>
                <p className="text-muted-foreground">No hay alertas activas en este momento.</p>
              </CardContent>
            </Card>
          ) : (
            filteredNotificaciones.map((notif) => (
              <Alert 
                key={notif.id_notificacion} 
                className={`${getAlertColor(notif.tipo, notif.semaforo)} ${
                  notif.leida ? 'opacity-60' : ''
                }`}
              >
                {getAlertIcon(notif.tipo)}
                <div className="flex-1">
                  <AlertDescription>
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold">{notif.nombre_insumo || notif.titulo}</span>
                          <Badge variant={getPriorityBadge(notif.tipo, notif.semaforo)} className="text-xs">
                            {notif.semaforo || notif.tipo}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {notif.tipo.replace('_', ' ')}
                          </Badge>
                        </div>
                        <p className="text-sm mb-1">{notif.mensaje}</p>
                        <div className="text-xs text-muted-foreground space-y-1">
                          {notif.cantidad_afectada && <div>Cantidad: {notif.cantidad_afectada}</div>}
                          {notif.dias_restantes !== undefined && <div>Días restantes: {notif.dias_restantes}</div>}
                          <div>Fecha: {new Date(notif.fecha_creacion).toLocaleDateString()}</div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 ml-4">
                        {!notif.leida && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleMarkAsRead(notif.id_notificacion)}
                          >
                            Marcar leída
                          </Button>
                        )}
                      </div>
                    </div>
                  </AlertDescription>
                </div>
              </Alert>
            ))
          )}
        </TabsContent>

        <TabsContent value="high">
          {filteredNotificaciones.filter(n => n.semaforo === 'ROJO' || n.tipo === 'VENCIDO').map((notif) => (
            <Alert key={notif.id_notificacion} className={getAlertColor(notif.tipo, notif.semaforo)}>
              {getAlertIcon(notif.tipo)}
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{notif.nombre_insumo || notif.titulo}</div>
                    <div className="text-sm">{notif.mensaje}</div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleMarkAsRead(notif.id_notificacion)}>
                    Marcar leída
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>

        <TabsContent value="expiring">
          {filteredNotificaciones.filter(n => n.tipo === 'VENCIMIENTO_PROXIMO' || n.tipo === 'USAR_HOY').map((notif) => (
            <Alert key={notif.id_notificacion} className={getAlertColor(notif.tipo, notif.semaforo)}>
              <Calendar className="h-4 w-4" />
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{notif.nombre_insumo || notif.titulo}</div>
                    <div className="text-sm">{notif.mensaje}</div>
                    {notif.dias_restantes !== undefined && (
                      <div className="text-xs text-muted-foreground">Días restantes: {notif.dias_restantes}</div>
                    )}
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleMarkAsRead(notif.id_notificacion)}>
                    Marcar leída
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>

        <TabsContent value="stock">
          {filteredNotificaciones.filter(n => n.tipo === 'STOCK_CRITICO').map((notif) => (
            <Alert key={notif.id_notificacion} className="border-orange-200 bg-orange-50">
              <Package className="h-4 w-4" />
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{notif.nombre_insumo || notif.titulo}</div>
                    <div className="text-sm">{notif.mensaje}</div>
                    {notif.cantidad_afectada && (
                      <div className="text-xs text-muted-foreground">Cantidad: {notif.cantidad_afectada}</div>
                    )}
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleMarkAsRead(notif.id_notificacion)}>
                    Marcar leída
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}