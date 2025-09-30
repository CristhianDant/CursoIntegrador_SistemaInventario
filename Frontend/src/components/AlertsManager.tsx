import { useState } from "react";
import { 
  AlertTriangle, 
  Calendar, 
  Package, 
  Bell, 
  CheckCircle, 
  X,
  Filter,
  RefreshCw
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";

interface AlertItem {
  id: number;
  type: 'low_stock' | 'expiring' | 'review_date';
  priority: 'high' | 'medium' | 'low';
  item: string;
  category: string;
  message: string;
  value: number;
  unit: string;
  date: string;
  dismissed: boolean;
  supplier?: string;
}

const mockAlerts: AlertItem[] = [
  {
    id: 1,
    type: 'review_date',
    priority: 'high',
    item: 'Crema batida',
    category: 'Lácteos',
    message: 'Fecha de vencimiento pasada - Revisar inmediatamente',
    value: 3,
    unit: 'litros',
    date: '2024-08-31',
    dismissed: false,
    supplier: 'Lácteos Premium'
  },
  {
    id: 2,
    type: 'expiring',
    priority: 'high',
    item: 'Leche entera',
    category: 'Lácteos',
    message: 'Por vencer en 2 días - Acción urgente requerida',
    value: 15,
    unit: 'litros',
    date: '2024-09-05',
    dismissed: false,
    supplier: 'Lácteos Premium'
  },
  {
    id: 3,
    type: 'expiring',
    priority: 'high',
    item: 'Huevos frescos',
    category: 'Proteínas',
    message: 'Por vencer en 3 días - Usar prioritariamente',
    value: 18,
    unit: 'docenas',
    date: '2024-09-06',
    dismissed: false,
    supplier: 'Granja Los Robles'
  },
  {
    id: 4,
    type: 'low_stock',
    priority: 'medium',
    item: 'Azúcar refinada',
    category: 'Endulzantes',
    message: 'Stock por debajo del mínimo (15kg)',
    value: 8,
    unit: 'kg',
    date: '2024-09-02',
    dismissed: false,
    supplier: 'Azucarera XYZ'
  },
  {
    id: 5,
    type: 'expiring',
    priority: 'medium',
    item: 'Mantequilla sin sal',
    category: 'Lácteos',
    message: 'Por vencer en 6 días - Planificar uso',
    value: 5,
    unit: 'kg',
    date: '2024-09-09',
    dismissed: false,
    supplier: 'Lácteos Premium'
  },
  {
    id: 6,
    type: 'low_stock',
    priority: 'medium',
    item: 'Vainilla natural',
    category: 'Especias',
    message: 'Stock por debajo del mínimo (5ml)',
    value: 3,
    unit: 'ml',
    date: '2024-09-01',
    dismissed: false,
    supplier: 'Especias Gourmet'
  }
];

export function AlertsManager() {
  const [alerts, setAlerts] = useState<AlertItem[]>(mockAlerts);
  const [selectedPriority, setSelectedPriority] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [showDismissed, setShowDismissed] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const filteredAlerts = alerts.filter(alert => {
    const matchesPriority = selectedPriority === "all" || alert.priority === selectedPriority;
    const matchesType = selectedType === "all" || alert.type === selectedType;
    const matchesDismissed = showDismissed || !alert.dismissed;
    
    return matchesPriority && matchesType && matchesDismissed;
  });

  const getAlertIcon = (type: AlertItem['type']) => {
    switch (type) {
      case 'review_date':
        return <AlertTriangle className="h-4 w-4" />;
      case 'expiring':
        return <Calendar className="h-4 w-4" />;
      case 'low_stock':
        return <Package className="h-4 w-4" />;
    }
  };

  const getAlertColor = (type: AlertItem['type'], priority: AlertItem['priority']) => {
    if (type === 'review_date') return 'border-red-200 bg-red-50';
    if (priority === 'high') return 'border-red-200 bg-red-50';
    if (priority === 'medium') return 'border-orange-200 bg-orange-50';
    return 'border-yellow-200 bg-yellow-50';
  };

  const getPriorityBadge = (priority: AlertItem['priority']) => {
    const variants = {
      high: 'destructive' as const,
      medium: 'secondary' as const,
      low: 'outline' as const
    };
    return variants[priority];
  };

  const getTypeBadge = (type: AlertItem['type']) => {
    const labels = {
      review_date: 'Revisar Fecha',
      expiring: 'Por Vencer',
      low_stock: 'Stock Bajo'
    };
    return labels[type];
  };

  const handleDismiss = (id: number) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === id ? { ...alert, dismissed: true } : alert
      )
    );
  };

  const handleRestore = (id: number) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === id ? { ...alert, dismissed: false } : alert
      )
    );
  };

  const getDashboardStats = () => {
    const active = alerts.filter(a => !a.dismissed);
    return {
      total: active.length,
      high: active.filter(a => a.priority === 'high').length,
      reviewDate: active.filter(a => a.type === 'review_date').length,
      expiring: active.filter(a => a.type === 'expiring').length,
      lowStock: active.filter(a => a.type === 'low_stock').length
    };
  };

  const stats = getDashboardStats();

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
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
        </div>
      </div>

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
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue placeholder="Tipo de alerta" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  <SelectItem value="review_date">Revisar fecha</SelectItem>
                  <SelectItem value="expiring">Por vencer</SelectItem>
                  <SelectItem value="low_stock">Stock bajo</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedPriority} onValueChange={setSelectedPriority}>
                <SelectTrigger>
                  <SelectValue placeholder="Prioridad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las prioridades</SelectItem>
                  <SelectItem value="high">Alta</SelectItem>
                  <SelectItem value="medium">Media</SelectItem>
                  <SelectItem value="low">Baja</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center space-x-2">
                <Switch 
                  id="show-dismissed" 
                  checked={showDismissed}
                  onCheckedChange={setShowDismissed}
                />
                <Label htmlFor="show-dismissed" className="text-sm">
                  Mostrar descartadas
                </Label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Alertas */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">Todas ({filteredAlerts.length})</TabsTrigger>
          <TabsTrigger value="high">
            Alta ({filteredAlerts.filter(a => a.priority === 'high').length})
          </TabsTrigger>
          <TabsTrigger value="expiring">
            Por Vencer ({filteredAlerts.filter(a => a.type === 'expiring').length})
          </TabsTrigger>
          <TabsTrigger value="review_date">
            Revisar ({filteredAlerts.filter(a => a.type === 'review_date').length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {filteredAlerts.length === 0 ? (
            <Card>
              <CardContent className="pt-8 text-center">
                <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">¡Todo bajo control!</h3>
                <p className="text-muted-foreground">No hay alertas activas en este momento.</p>
              </CardContent>
            </Card>
          ) : (
            filteredAlerts.map((alert) => (
              <Alert 
                key={alert.id} 
                className={`${getAlertColor(alert.type, alert.priority)} ${
                  alert.dismissed ? 'opacity-60' : ''
                }`}
              >
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <AlertDescription>
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold">{alert.item}</span>
                          <Badge variant={getPriorityBadge(alert.priority)} className="text-xs">
                            {alert.priority.toUpperCase()}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {getTypeBadge(alert.type)}
                          </Badge>
                        </div>
                        <p className="text-sm mb-1">{alert.message}</p>
                        <div className="text-xs text-muted-foreground space-y-1">
                          <div>Stock actual: {alert.value} {alert.unit}</div>
                          <div>Categoría: {alert.category}</div>
                          <div>Proveedor: {alert.supplier}</div>
                          <div>Fecha: {new Date(alert.date).toLocaleDateString()}</div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 ml-4">
                        {!alert.dismissed ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDismiss(alert.id)}
                          >
                            Descartar
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRestore(alert.id)}
                          >
                            Restaurar
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
          {filteredAlerts.filter(a => a.priority === 'high').map((alert) => (
            <Alert key={alert.id} className={getAlertColor(alert.type, alert.priority)}>
              {getAlertIcon(alert.type)}
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{alert.item}</div>
                    <div className="text-sm">{alert.message}</div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleDismiss(alert.id)}>
                    Descartar
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>

        <TabsContent value="expiring">
          {filteredAlerts.filter(a => a.type === 'expiring').map((alert) => (
            <Alert key={alert.id} className={getAlertColor(alert.type, alert.priority)}>
              <Calendar className="h-4 w-4" />
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold">{alert.item}</div>
                    <div className="text-sm">{alert.message}</div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleDismiss(alert.id)}>
                    Descartar
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>

        <TabsContent value="review_date">
          {filteredAlerts.filter(a => a.type === 'review_date').map((alert) => (
            <Alert key={alert.id} className="border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-red-700">{alert.item}</div>
                    <div className="text-sm text-red-600">{alert.message}</div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => handleDismiss(alert.id)}>
                    Descartar
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