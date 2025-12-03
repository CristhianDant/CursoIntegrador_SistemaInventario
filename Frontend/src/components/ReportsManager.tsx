import { useState, useEffect } from "react";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Filter,
  Download,
  Eye,
  Loader2,
  RefreshCw
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Alert, AlertDescription } from "./ui/alert";
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
import { API_BASE_URL } from "../constants";

// Interfaces basadas en los schemas del backend
interface ProductoABC {
  id_producto: number;
  codigo: string;
  nombre: string;
  cantidad_vendida: number;
  monto_total: number;
  porcentaje_ventas: number;
  porcentaje_acumulado: number;
  clasificacion: string;
  frecuencia_control: string;
}

interface ReporteABCResponse {
  fecha_inicio: string;
  fecha_fin: string;
  total_ventas: number;
  total_productos: number;
  resumen: Record<string, any>;
  productos_a: ProductoABC[];
  productos_b: ProductoABC[];
  productos_c: ProductoABC[];
}

interface KPIValue {
  nombre: string;
  valor: number;
  unidad: string;
  meta: number;
  cumple_meta: boolean;
  tendencia?: string;
  detalle?: string;
}

interface KPIsResponse {
  fecha: string;
  merma_diaria: KPIValue;
  productos_vencidos_hoy: KPIValue;
  cumplimiento_fefo: KPIValue;
  stock_critico: KPIValue;
  rotacion_inventario: KPIValue;
  kpis_cumplidos: number;
  kpis_totales: number;
  porcentaje_cumplimiento: number;
}

interface ItemRotacion {
  id: number;
  codigo: string;
  nombre: string;
  tipo: string;
  stock_actual: number;
  unidad_medida: string;
  consumo_periodo: number;
  dias_stock: number;
  rotacion_periodo: number;
  rotacion_anualizada: number;
  clasificacion: string;
}

interface RotacionResponse {
  fecha_inicio: string;
  fecha_fin: string;
  dias_periodo: number;
  rotacion_promedio_anual: number;
  meta_rotacion_anual: number;
  cumple_meta: boolean;
  total_items: number;
  items_alta_rotacion: number;
  items_media_rotacion: number;
  items_baja_rotacion: number;
  insumos: ItemRotacion[];
  productos_terminados: ItemRotacion[];
}

// Mock data solo como fallback cuando no hay datos del backend
const monthlyConsumption = [
  { month: 'Ene', harina: 120, azucar: 80, huevos: 200, mantequilla: 45 },
  { month: 'Feb', harina: 140, azucar: 95, huevos: 220, mantequilla: 52 },
  { month: 'Mar', harina: 130, azucar: 85, huevos: 210, mantequilla: 48 },
  { month: 'Abr', harina: 155, azucar: 110, huevos: 240, mantequilla: 58 },
  { month: 'May', harina: 165, azucar: 120, huevos: 260, mantequilla: 62 },
  { month: 'Jun', harina: 150, azucar: 105, huevos: 245, mantequilla: 55 },
];

const COLORS = ['#f97316', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'];

export function ReportsManager() {
  const [selectedPeriod, setSelectedPeriod] = useState("6months");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setMonth(date.getMonth() - 1);
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  
  // Estados para datos del backend
  const [kpis, setKpis] = useState<KPIsResponse | null>(null);
  const [abcReport, setAbcReport] = useState<ReporteABCResponse | null>(null);
  const [rotacion, setRotacion] = useState<RotacionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Actualizar fechas según período seleccionado
  useEffect(() => {
    const now = new Date();
    let start = new Date();
    
    switch (selectedPeriod) {
      case "1month":
        start.setMonth(now.getMonth() - 1);
        break;
      case "3months":
        start.setMonth(now.getMonth() - 3);
        break;
      case "6months":
        start.setMonth(now.getMonth() - 6);
        break;
      case "1year":
        start.setFullYear(now.getFullYear() - 1);
        break;
      case "custom":
        return; // No actualizar si es personalizado
    }
    
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(now.toISOString().split('T')[0]);
  }, [selectedPeriod]);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const today = new Date().toISOString().split('T')[0];
      
      const [kpisRes, abcRes, rotacionRes] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/v1/reportes/kpis?fecha=${today}`),
        fetch(`${API_BASE_URL}/v1/reportes/abc?fecha_inicio=${startDate}&fecha_fin=${endDate}`),
        fetch(`${API_BASE_URL}/v1/reportes/rotacion?fecha_inicio=${startDate}&fecha_fin=${endDate}`)
      ]);

      if (kpisRes.status === 'fulfilled' && kpisRes.value.ok) {
        const data = await kpisRes.value.json();
        setKpis(data.data || data);
      }

      if (abcRes.status === 'fulfilled' && abcRes.value.ok) {
        const data = await abcRes.value.json();
        setAbcReport(data.data || data);
      }

      if (rotacionRes.status === 'fulfilled' && rotacionRes.value.ok) {
        const data = await rotacionRes.value.json();
        setRotacion(data.data || data);
      }

    } catch (err) {
      console.error('Error fetching reports:', err);
      setError('Error al cargar los reportes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [startDate, endDate]);

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'subiendo':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'bajando':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full" />;
    }
  };

  // Preparar datos para gráfico de distribución ABC
  const abcDistribution = abcReport ? [
    { name: 'Categoría A', value: abcReport.productos_a.length, color: '#10b981' },
    { name: 'Categoría B', value: abcReport.productos_b.length, color: '#f59e0b' },
    { name: 'Categoría C', value: abcReport.productos_c.length, color: '#ef4444' },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Reportes y Análisis</h2>
          <p className="text-muted-foreground">Análisis detallado de consumo, costos y rendimiento</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchReports} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Exportar Reporte
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-600">{error}</AlertDescription>
        </Alert>
      )}

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
      <Tabs defaultValue="kpis" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="kpis">KPIs</TabsTrigger>
          <TabsTrigger value="abc">Análisis ABC</TabsTrigger>
          <TabsTrigger value="rotacion">Rotación</TabsTrigger>
          <TabsTrigger value="consumption">Consumo</TabsTrigger>
        </TabsList>

        {/* KPIs Dashboard */}
        <TabsContent value="kpis" className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : kpis ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${kpis.merma_diaria.cumple_meta ? 'text-green-600' : 'text-red-600'}`}>
                        {Number(kpis.merma_diaria.valor).toFixed(1)}{kpis.merma_diaria.unidad}
                      </div>
                      <p className="text-sm text-muted-foreground">{kpis.merma_diaria.nombre}</p>
                      <Badge variant={kpis.merma_diaria.cumple_meta ? 'default' : 'destructive'} className="mt-1">
                        Meta: &lt;{kpis.merma_diaria.meta}{kpis.merma_diaria.unidad}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${kpis.productos_vencidos_hoy.cumple_meta ? 'text-green-600' : 'text-red-600'}`}>
                        {kpis.productos_vencidos_hoy.valor}
                      </div>
                      <p className="text-sm text-muted-foreground">{kpis.productos_vencidos_hoy.nombre}</p>
                      <Badge variant={kpis.productos_vencidos_hoy.cumple_meta ? 'default' : 'destructive'} className="mt-1">
                        Meta: {kpis.productos_vencidos_hoy.meta}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${kpis.cumplimiento_fefo.cumple_meta ? 'text-green-600' : 'text-red-600'}`}>
                        {Number(kpis.cumplimiento_fefo.valor).toFixed(1)}{kpis.cumplimiento_fefo.unidad}
                      </div>
                      <p className="text-sm text-muted-foreground">{kpis.cumplimiento_fefo.nombre}</p>
                      <Badge variant={kpis.cumplimiento_fefo.cumple_meta ? 'default' : 'destructive'} className="mt-1">
                        Meta: &gt;{kpis.cumplimiento_fefo.meta}{kpis.cumplimiento_fefo.unidad}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${kpis.stock_critico.cumple_meta ? 'text-green-600' : 'text-orange-600'}`}>
                        {kpis.stock_critico.valor}
                      </div>
                      <p className="text-sm text-muted-foreground">{kpis.stock_critico.nombre}</p>
                      <Badge variant={kpis.stock_critico.cumple_meta ? 'default' : 'secondary'} className="mt-1">
                        Meta: &lt;{kpis.stock_critico.meta}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${kpis.rotacion_inventario.cumple_meta ? 'text-green-600' : 'text-orange-600'}`}>
                        {Number(kpis.rotacion_inventario.valor).toFixed(1)}
                      </div>
                      <p className="text-sm text-muted-foreground">{kpis.rotacion_inventario.nombre}</p>
                      <Badge variant={kpis.rotacion_inventario.cumple_meta ? 'default' : 'secondary'} className="mt-1">
                        Meta: &gt;{kpis.rotacion_inventario.meta}/año
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Resumen de Cumplimiento</h3>
                      <p className="text-muted-foreground">
                        {kpis.kpis_cumplidos} de {kpis.kpis_totales} KPIs cumplidos
                      </p>
                    </div>
                    <div className={`text-3xl font-bold ${Number(kpis.porcentaje_cumplimiento) >= 80 ? 'text-green-600' : 'text-orange-600'}`}>
                      {Number(kpis.porcentaje_cumplimiento).toFixed(0)}%
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="pt-8 text-center">
                <p className="text-muted-foreground">No hay datos de KPIs disponibles</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Análisis ABC */}
        <TabsContent value="abc" className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : abcReport ? (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Distribución ABC</CardTitle>
                    <CardDescription>
                      Clasificación de productos por contribución a ventas
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={abcDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {abcDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Resumen del Análisis</CardTitle>
                    <CardDescription>
                      Período: {abcReport.fecha_inicio} a {abcReport.fecha_fin}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span>Total Ventas:</span>
                      <span className="font-bold">${Number(abcReport.total_ventas).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Productos:</span>
                      <span className="font-bold">{abcReport.total_productos}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Categoría A (70% ventas):</span>
                      <Badge className="bg-green-100 text-green-800">{abcReport.productos_a.length} productos</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Categoría B (20% ventas):</span>
                      <Badge className="bg-yellow-100 text-yellow-800">{abcReport.productos_b.length} productos</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Categoría C (10% ventas):</span>
                      <Badge className="bg-red-100 text-red-800">{abcReport.productos_c.length} productos</Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Productos Categoría A - Control DIARIO</CardTitle>
                  <CardDescription>Productos que representan el 70% de las ventas</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Código</TableHead>
                        <TableHead>Producto</TableHead>
                        <TableHead>Cantidad Vendida</TableHead>
                        <TableHead>Monto Total</TableHead>
                        <TableHead>% Ventas</TableHead>
                        <TableHead>% Acumulado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {abcReport.productos_a.slice(0, 10).map((producto) => (
                        <TableRow key={producto.id_producto}>
                          <TableCell>{producto.codigo}</TableCell>
                          <TableCell className="font-medium">{producto.nombre}</TableCell>
                          <TableCell>{Number(producto.cantidad_vendida).toFixed(0)}</TableCell>
                          <TableCell>${Number(producto.monto_total).toLocaleString()}</TableCell>
                          <TableCell>{Number(producto.porcentaje_ventas).toFixed(1)}%</TableCell>
                          <TableCell>{Number(producto.porcentaje_acumulado).toFixed(1)}%</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="pt-8 text-center">
                <p className="text-muted-foreground">No hay datos de análisis ABC disponibles para el período seleccionado</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Rotación de Inventario */}
        <TabsContent value="rotacion" className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : rotacion ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${rotacion.cumple_meta ? 'text-green-600' : 'text-orange-600'}`}>
                        {Number(rotacion.rotacion_promedio_anual).toFixed(1)}x
                      </div>
                      <p className="text-sm text-muted-foreground">Rotación Promedio Anual</p>
                      <Badge variant={rotacion.cumple_meta ? 'default' : 'secondary'} className="mt-1">
                        Meta: {rotacion.meta_rotacion_anual}x/año
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{rotacion.items_alta_rotacion}</div>
                      <p className="text-sm text-muted-foreground">Alta Rotación</p>
                      <p className="text-xs text-muted-foreground">≥12 veces/año</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">{rotacion.items_media_rotacion}</div>
                      <p className="text-sm text-muted-foreground">Media Rotación</p>
                      <p className="text-xs text-muted-foreground">6-12 veces/año</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{rotacion.items_baja_rotacion}</div>
                      <p className="text-sm text-muted-foreground">Baja Rotación</p>
                      <p className="text-xs text-muted-foreground">&lt;6 veces/año</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Detalle de Rotación - Insumos</CardTitle>
                  <CardDescription>
                    Período: {rotacion.fecha_inicio} a {rotacion.fecha_fin} ({rotacion.dias_periodo} días)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Código</TableHead>
                        <TableHead>Insumo</TableHead>
                        <TableHead>Stock Actual</TableHead>
                        <TableHead>Consumo</TableHead>
                        <TableHead>Días Stock</TableHead>
                        <TableHead>Rotación Anual</TableHead>
                        <TableHead>Clasificación</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {rotacion.insumos.slice(0, 15).map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>{item.codigo}</TableCell>
                          <TableCell className="font-medium">{item.nombre}</TableCell>
                          <TableCell>{Number(item.stock_actual).toFixed(1)} {item.unidad_medida}</TableCell>
                          <TableCell>{Number(item.consumo_periodo).toFixed(1)}</TableCell>
                          <TableCell>{Number(item.dias_stock).toFixed(0)}</TableCell>
                          <TableCell>{Number(item.rotacion_anualizada).toFixed(1)}x</TableCell>
                          <TableCell>
                            <Badge variant={
                              item.clasificacion === 'alta' ? 'default' :
                              item.clasificacion === 'media' ? 'secondary' : 'destructive'
                            }>
                              {item.clasificacion}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="pt-8 text-center">
                <p className="text-muted-foreground">No hay datos de rotación disponibles para el período seleccionado</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Reporte de Consumo (mantiene datos mock por ahora) */}
        {/* Reporte de Consumo (mantiene datos mock por ahora) */}
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
                <CardTitle>Análisis de Costos por Mes</CardTitle>
                <CardDescription>
                  Evolución del gasto mensual en insumos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyConsumption.map((item) => ({
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
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}