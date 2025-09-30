import { useState } from "react";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Filter,
  Download,
  Eye
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

// Mock data para los reportes
const monthlyConsumption = [
  { month: 'Ene', harina: 120, azucar: 80, huevos: 200, mantequilla: 45 },
  { month: 'Feb', harina: 140, azucar: 95, huevos: 220, mantequilla: 52 },
  { month: 'Mar', harina: 130, azucar: 85, huevos: 210, mantequilla: 48 },
  { month: 'Abr', harina: 155, azucar: 110, huevos: 240, mantequilla: 58 },
  { month: 'May', harina: 165, azucar: 120, huevos: 260, mantequilla: 62 },
  { month: 'Jun', harina: 150, azucar: 105, huevos: 245, mantequilla: 55 },
];

const categoryDistribution = [
  { name: 'Harinas', value: 35, color: '#f97316' },
  { name: 'Lácteos', value: 25, color: '#3b82f6' },
  { name: 'Endulzantes', value: 20, color: '#10b981' },
  { name: 'Proteínas', value: 15, color: '#f59e0b' },
  { name: 'Otros', value: 5, color: '#8b5cf6' },
];

const wasteData = [
  { month: 'Ene', merma: 2.1, valor: 1200 },
  { month: 'Feb', merma: 1.8, valor: 1050 },
  { month: 'Mar', merma: 2.5, valor: 1450 },
  { month: 'Abr', merma: 1.9, valor: 1100 },
  { month: 'May', merma: 2.3, valor: 1300 },
  { month: 'Jun', merma: 1.6, valor: 950 },
];

const topIngredients = [
  { ingredient: 'Harina de trigo', consumption: 165, unit: 'kg', cost: 198, trend: 'up' },
  { ingredient: 'Azúcar refinada', consumption: 120, unit: 'kg', cost: 300, trend: 'up' },
  { ingredient: 'Huevos frescos', consumption: 260, unit: 'docenas', cost: 1040, trend: 'down' },
  { ingredient: 'Mantequilla', consumption: 62, unit: 'kg', cost: 527, trend: 'up' },
  { ingredient: 'Chocolate negro', consumption: 45, unit: 'kg', cost: 675, trend: 'stable' },
];

const supplierPerformance = [
  { supplier: 'Molinos ABC', items: 8, onTime: 95, quality: 98, totalCost: 2400 },
  { supplier: 'Lácteos Premium', items: 5, onTime: 88, quality: 96, totalCost: 1850 },
  { supplier: 'Granja Los Robles', items: 3, onTime: 92, quality: 99, totalCost: 1200 },
  { supplier: 'Azucarera XYZ', items: 4, onTime: 96, quality: 94, totalCost: 980 },
  { supplier: 'Cacao Gourmet', items: 6, onTime: 85, quality: 97, totalCost: 1620 },
];

export function ReportsManager() {
  const [selectedPeriod, setSelectedPeriod] = useState("6months");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full" />;
    }
  };

  const COLORS = ['#f97316', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Reportes y Análisis</h2>
          <p className="text-muted-foreground">Análisis detallado de consumo, costos y rendimiento</p>
        </div>
        
        <Button>
          <Download className="h-4 w-4 mr-2" />
          Exportar Reporte
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Período</Label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1month">Último mes</SelectItem>
                  <SelectItem value="3months">Últimos 3 meses</SelectItem>
                  <SelectItem value="6months">Últimos 6 meses</SelectItem>
                  <SelectItem value="1year">Último año</SelectItem>
                  <SelectItem value="custom">Personalizado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Categoría</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las categorías</SelectItem>
                  <SelectItem value="harinas">Harinas</SelectItem>
                  <SelectItem value="lacteos">Lácteos</SelectItem>
                  <SelectItem value="endulzantes">Endulzantes</SelectItem>
                  <SelectItem value="proteinas">Proteínas</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {selectedPeriod === 'custom' && (
              <>
                <div className="space-y-2">
                  <Label>Fecha Inicio</Label>
                  <Input 
                    type="date" 
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Fecha Fin</Label>
                  <Input 
                    type="date" 
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs de reportes */}
      <Tabs defaultValue="consumption" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="consumption">Consumo</TabsTrigger>
          <TabsTrigger value="waste">Merma</TabsTrigger>
          <TabsTrigger value="suppliers">Proveedores</TabsTrigger>
          <TabsTrigger value="financial">Financiero</TabsTrigger>
        </TabsList>

        {/* Reporte de Consumo */}
        <TabsContent value="consumption" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de consumo mensual */}
            <Card>
              <CardHeader>
                <CardTitle>Consumo Mensual por Ingrediente</CardTitle>
                <CardDescription>
                  Tendencia de consumo de los principales insumos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyConsumption}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="harina" stroke="#f97316" strokeWidth={2} />
                    <Line type="monotone" dataKey="azucar" stroke="#3b82f6" strokeWidth={2} />
                    <Line type="monotone" dataKey="huevos" stroke="#10b981" strokeWidth={2} />
                    <Line type="monotone" dataKey="mantequilla" stroke="#f59e0b" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Distribución por categorías */}
            <Card>
              <CardHeader>
                <CardTitle>Distribución por Categorías</CardTitle>
                <CardDescription>
                  Porcentaje de uso por tipo de insumo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Top ingredientes */}
          <Card>
            <CardHeader>
              <CardTitle>Top Ingredientes por Consumo</CardTitle>
              <CardDescription>
                Los ingredientes más utilizados este período
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ingrediente</TableHead>
                    <TableHead>Consumo</TableHead>
                    <TableHead>Costo Total</TableHead>
                    <TableHead>Tendencia</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {topIngredients.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{item.ingredient}</TableCell>
                      <TableCell>{item.consumption} {item.unit}</TableCell>
                      <TableCell>${item.cost}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          {getTrendIcon(item.trend)}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reporte de Merma */}
        <TabsContent value="waste" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">2.1%</div>
                  <p className="text-sm text-muted-foreground">Promedio de merma</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">$7.2K</div>
                  <p className="text-sm text-muted-foreground">Pérdidas totales</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">-15%</div>
                  <p className="text-sm text-muted-foreground">vs. período anterior</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Evolución de la Merma</CardTitle>
              <CardDescription>
                Porcentaje de merma y valor monetario por mes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={wasteData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Bar yAxisId="left" dataKey="merma" fill="#f97316" name="% Merma" />
                  <Bar yAxisId="right" dataKey="valor" fill="#3b82f6" name="Valor ($)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reporte de Proveedores */}
        <TabsContent value="suppliers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Rendimiento de Proveedores</CardTitle>
              <CardDescription>
                Evaluación del desempeño de cada proveedor
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Proveedor</TableHead>
                    <TableHead>Items</TableHead>
                    <TableHead>Puntualidad</TableHead>
                    <TableHead>Calidad</TableHead>
                    <TableHead>Costo Total</TableHead>
                    <TableHead>Evaluación</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {supplierPerformance.map((supplier, index) => {
                    const avgScore = (supplier.onTime + supplier.quality) / 2;
                    const getScoreBadge = (score: number) => {
                      if (score >= 95) return <Badge className="bg-green-100 text-green-800">Excelente</Badge>;
                      if (score >= 90) return <Badge className="bg-blue-100 text-blue-800">Bueno</Badge>;
                      if (score >= 85) return <Badge className="bg-yellow-100 text-yellow-800">Regular</Badge>;
                      return <Badge className="bg-red-100 text-red-800">Deficiente</Badge>;
                    };

                    return (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{supplier.supplier}</TableCell>
                        <TableCell>{supplier.items}</TableCell>
                        <TableCell>{supplier.onTime}%</TableCell>
                        <TableCell>{supplier.quality}%</TableCell>
                        <TableCell>${supplier.totalCost.toLocaleString()}</TableCell>
                        <TableCell>{getScoreBadge(avgScore)}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reporte Financiero */}
        <TabsContent value="financial" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">$15.4K</div>
                  <p className="text-sm text-muted-foreground">Valor Inventario</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">$8.2K</div>
                  <p className="text-sm text-muted-foreground">Compras del Mes</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">$1.2K</div>
                  <p className="text-sm text-muted-foreground">Pérdidas por Merma</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">7.8%</div>
                  <p className="text-sm text-muted-foreground">ROI Inventario</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Análisis de Costos por Categoría</CardTitle>
              <CardDescription>
                Distribución del gasto por tipo de insumo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyConsumption.map((item, index) => ({
                  month: item.month,
                  total: (item.harina * 1.2) + (item.azucar * 2.5) + (item.huevos * 4.0) + (item.mantequilla * 8.5)
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}`, 'Costo Total']} />
                  <Bar dataKey="total" fill="#f97316" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}