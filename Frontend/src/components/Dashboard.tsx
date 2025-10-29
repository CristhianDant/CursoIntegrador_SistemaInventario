import { AlertTriangle, PackageX, TrendingDown } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";

// Datos mínimos necesarios para las secciones que el usuario quiere mantener
const mockData = {
  monthlyWaste: 2.3,
  recentAlerts: [
    { id: 1, type: 'stock', item: 'Harina de trigo', level: 2, unit: 'kg' },
    { id: 2, type: 'expiry', item: 'Leche fresca', days: 2, unit: 'litros' },
    { id: 3, type: 'stock', item: 'Azúcar refinada', level: 1.5, unit: 'kg' },
    { id: 4, type: 'expiry', item: 'Huevos frescos', days: 1, unit: 'docenas' },
  ],
  topIngredients: [
    { name: 'Harina de trigo', stock: 25, total: 50, unit: 'kg' },
    { name: 'Azúcar refinada', stock: 15, total: 30, unit: 'kg' },
    { name: 'Mantequilla', stock: 8, total: 15, unit: 'kg' },
    { name: 'Huevos', stock: 20, total: 40, unit: 'docenas' },
    { name: 'Leche', stock: 12, total: 25, unit: 'litros' },
  ]
};

export function Dashboard() {
  return (
    <div className="space-y-6">
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
            {mockData.recentAlerts.map((alert) => (
              <Alert key={alert.id} className={
                alert.type === 'expiry' ? 'border-red-200 bg-red-50' : 'border-orange-200 bg-orange-50'
              }>
                <AlertTriangle className={`h-4 w-4 ${
                  alert.type === 'expiry' ? 'text-red-600' : 'text-orange-600'
                }`} />
                <AlertDescription>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{alert.item}</span>
                    <Badge variant={alert.type === 'expiry' ? 'destructive' : 'secondary'}>
                      {alert.type === 'expiry' 
                        ? `Por vencer en ${alert.days} días`
                        : `Stock: ${alert.level} ${alert.unit}`
                      }
                    </Badge>
                  </div>
                </AlertDescription>
              </Alert>
            ))}
          </CardContent>
        </Card>

        {/* Insumos principales */}
        <Card>
          <CardHeader>
            <CardTitle>Insumos Principales</CardTitle>
            <CardDescription>
              Estado actual del stock de ingredientes clave
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockData.topIngredients.map((ingredient, index) => {
              const percentage = (ingredient.stock / ingredient.total) * 100;
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{ingredient.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {ingredient.stock}/{ingredient.total} {ingredient.unit}
                    </span>
                  </div>
                  <Progress 
                    value={percentage} 
                    className={`h-2 ${
                      percentage < 30 ? 'text-red-500' : 
                      percentage < 60 ? 'text-orange-500' : 'text-green-500'
                    }`}
                  />
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Resumen de merma */}
      <Card>
        <CardHeader>
          <CardTitle>Resumen de Merma - Este Mes</CardTitle>
          <CardDescription>
            Análisis de productos perdidos por vencimiento
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-red-100 rounded-full">
              <PackageX className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                ${mockData.monthlyWaste.toFixed(1)}K
              </div>
              <p className="text-sm text-muted-foreground">
                Pérdidas por vencimiento este mes
              </p>
            </div>
            <div className="ml-auto text-right">
              <div className="flex items-center text-green-600">
                <TrendingDown className="h-4 w-4 mr-1" />
                <span className="text-sm font-medium">-15%</span>
              </div>
              <p className="text-xs text-muted-foreground">vs. mes anterior</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}