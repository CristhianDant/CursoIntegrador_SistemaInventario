import { useState, useEffect } from "react";
import { AlertTriangle, PackageX, TrendingDown, ShoppingCart, Loader2, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Button } from "./ui/button";
import { API_BASE_URL } from "../constants";

// Interfaces para los datos del backend
interface AlertaNotificacion {
  id_notificacion: number;
  tipo: 'STOCK_CRITICO' | 'VENCIMIENTO_PROXIMO' | 'USAR_HOY' | 'VENCIDO';
  titulo: string;
  mensaje: string;
  nombre_insumo?: string;
  dias_restantes?: number;
  cantidad_afectada?: string;
  semaforo?: 'VERDE' | 'AMARILLO' | 'ROJO';
}

interface InsumoStockCritico {
  id_insumo: number;
  codigo: string;
  nombre: string;
  unidad_medida: string;
  stock_actual: number;
  stock_minimo: number;
  porcentaje_stock: number;
}

interface ResumenAlertas {
  total_no_leidas: number;
  por_tipo: Record<string, number>;
}

interface DashboardData {
  pendingOrders: number;
  monthlyWaste: number;
  stockCriticoCount: number;
  alertas: AlertaNotificacion[];
  insumosStockCritico: InsumoStockCritico[];
  loading: boolean;
  error: string | null;
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData>({
    pendingOrders: 0,
    monthlyWaste: 0,
    stockCriticoCount: 0,
    alertas: [],
    insumosStockCritico: [],
    loading: true,
    error: null
  });

  const fetchDashboardData = async () => {
    setData(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      // Fetch en paralelo para mejor rendimiento
      const [ordenesRes, alertasRes, stockCriticoRes, notificacionesRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/v1/ordenes_compra?activas_solo=true`),
        fetch(`${API_BASE_URL}/v1/alertas/resumen`),
        fetch(`${API_BASE_URL}/v1/alertas/stock-critico`),
        fetch(`${API_BASE_URL}/v1/alertas/notificaciones?limit=10&solo_no_leidas=true`)
      ]);

      let pendingOrders = 0;
      let stockCriticoCount = 0;
      let alertas: AlertaNotificacion[] = [];
      let insumosStockCritico: InsumoStockCritico[] = [];

      // Procesar órdenes pendientes
      if (ordenesRes.status === 'fulfilled' && ordenesRes.value.ok) {
        const ordenesData = await ordenesRes.value.json();
        const ordenes = ordenesData.data || ordenesData || [];
        pendingOrders = ordenes.filter((o: any) => 
          o.estado === 'PENDIENTE' || o.estado === 'ENVIADA'
        ).length;
      }

      // Procesar stock crítico
      if (stockCriticoRes.status === 'fulfilled' && stockCriticoRes.value.ok) {
        const stockData = await stockCriticoRes.value.json();
        const items = stockData.items || stockData.data?.items || [];
        insumosStockCritico = items.slice(0, 5);
        stockCriticoCount = stockData.total_sin_stock + stockData.total_bajo_minimo || items.length;
      }

      // Procesar notificaciones/alertas
      if (notificacionesRes.status === 'fulfilled' && notificacionesRes.value.ok) {
        const notifData = await notificacionesRes.value.json();
        alertas = (notifData.data || notifData || []).slice(0, 4);
      }

      setData({
        pendingOrders,
        monthlyWaste: 2.3, // TODO: Conectar con endpoint de mermas cuando esté disponible
        stockCriticoCount,
        alertas,
        insumosStockCritico,
        loading: false,
        error: null
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setData(prev => ({
        ...prev,
        loading: false,
        error: 'Error al cargar los datos del dashboard'
      }));
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Actualizar cada 5 minutos
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getAlertType = (tipo: string): 'stock' | 'expiry' => {
    return tipo === 'STOCK_CRITICO' ? 'stock' : 'expiry';
  };

  const getAlertBadgeText = (alerta: AlertaNotificacion): string => {
    if (alerta.tipo === 'STOCK_CRITICO') {
      return `Stock: ${alerta.cantidad_afectada || 'Bajo'}`;
    }
    if (alerta.dias_restantes !== undefined) {
      return alerta.dias_restantes <= 0 
        ? 'Vencido' 
        : `Por vencer en ${alerta.dias_restantes} días`;
    }
    return alerta.mensaje;
  };

  if (data.loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Cargando dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con botón de actualizar */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Dashboard</h2>
          <p className="text-muted-foreground">Resumen del estado del inventario</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchDashboardData} disabled={data.loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${data.loading ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {data.error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-600">{data.error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Órdenes de Compra Pendientes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Órdenes Pendientes
            </CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.pendingOrders}</div>
            <p className="text-xs text-muted-foreground">
              Órdenes de compra esperando aprobación o entrega.
            </p>
          </CardContent>
        </Card>

        {/* Merma del Mes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Merma del Mes</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.monthlyWaste}%</div>
            <p className="text-xs text-muted-foreground">
              Respecto al total de insumos del mes anterior.
            </p>
          </CardContent>
        </Card>

        {/* Insumos Agotándose */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Insumos Agotándose</CardTitle>
            <PackageX className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.stockCriticoCount}</div>
            <p className="text-xs text-muted-foreground">
              Insumos con niveles de stock bajos.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alertas recientes */}
        <Card>
          <CardHeader>
            <CardTitle>Alertas Recientes</CardTitle>
            <CardDescription>
              Insumos que requieren atención inmediata
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.alertas.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No hay alertas pendientes
              </p>
            ) : (
              data.alertas.map((alerta) => {
                const alertType = getAlertType(alerta.tipo);
                return (
                  <Alert key={alerta.id_notificacion} className={
                    alertType === 'expiry' ? 'border-red-200 bg-red-50' : 'border-orange-200 bg-orange-50'
                  }>
                    <AlertTriangle className={`h-4 w-4 ${
                      alertType === 'expiry' ? 'text-red-600' : 'text-orange-600'
                    }`} />
                    <AlertDescription>
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{alerta.nombre_insumo || alerta.titulo}</span>
                        <Badge variant={alertType === 'expiry' ? 'destructive' : 'secondary'}>
                          {getAlertBadgeText(alerta)}
                        </Badge>
                      </div>
                    </AlertDescription>
                  </Alert>
                );
              })
            )}
          </CardContent>
        </Card>

        {/* Insumos principales con stock crítico */}
        <Card>
          <CardHeader>
            <CardTitle>Insumos con Stock Crítico</CardTitle>
            <CardDescription>
              Estado actual del stock de ingredientes con niveles bajos
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.insumosStockCritico.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Todos los insumos tienen stock adecuado
              </p>
            ) : (
              data.insumosStockCritico.map((insumo) => {
                const percentage = Math.min(insumo.porcentaje_stock, 100);
                return (
                  <div key={insumo.id_insumo} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">{insumo.nombre}</span>
                      <span className="text-sm text-muted-foreground">
                        {insumo.stock_actual}/{insumo.stock_minimo} {insumo.unidad_medida}
                      </span>
                    </div>
                    <Progress 
                      value={percentage} 
                      className={`h-2 ${
                        percentage < 30 ? '[&>div]:bg-red-500' : 
                        percentage < 60 ? '[&>div]:bg-orange-500' : '[&>div]:bg-green-500'
                      }`}
                    />
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}