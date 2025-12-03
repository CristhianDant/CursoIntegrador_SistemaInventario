import { useState, useEffect } from "react";
import {
  ShoppingCart,
  Plus,
  Minus,
  Trash2,
  CreditCard,
  Banknote,
  ArrowLeftRight,
  Loader2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Tag,
  Package
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Separator } from "./ui/separator";
import { ScrollArea } from "./ui/scroll-area";
import { API_BASE_URL } from "../constants";

// Interfaces basadas en los schemas del backend
interface ProductoDisponible {
  id_producto: number;
  codigo_producto: string;
  nombre: string;
  descripcion?: string;
  stock_actual: number;
  precio_venta: number;
  dias_desde_produccion?: number;
  descuento_sugerido: number;
}

interface CartItem {
  producto: ProductoDisponible;
  cantidad: number;
  precio_unitario: number;
  descuento_porcentaje: number;
}

interface VentaResponse {
  id_venta: number;
  numero_venta: string;
  fecha_venta: string;
  total: number;
  metodo_pago: string;
}

export function SalesPointManager() {
  const [productos, setProductos] = useState<ProductoDisponible[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [metodoPago, setMetodoPago] = useState("efectivo");
  const [observaciones, setObservaciones] = useState("");
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [lastVenta, setLastVenta] = useState<VentaResponse | null>(null);

  const fetchProductos = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/ventas/productos-disponibles`);
      if (response.ok) {
        const data = await response.json();
        setProductos(data.data || data || []);
      } else {
        throw new Error('Error al cargar productos');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Error al cargar los productos disponibles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  // Filtrar productos por búsqueda
  const filteredProductos = productos.filter(p =>
    p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.codigo_producto.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Agregar producto al carrito
  const addToCart = (producto: ProductoDisponible) => {
    const existingItem = cart.find(item => item.producto.id_producto === producto.id_producto);
    
    if (existingItem) {
      if (existingItem.cantidad < producto.stock_actual) {
        setCart(cart.map(item =>
          item.producto.id_producto === producto.id_producto
            ? { ...item, cantidad: item.cantidad + 1 }
            : item
        ));
      }
    } else {
      setCart([...cart, {
        producto,
        cantidad: 1,
        precio_unitario: producto.precio_venta,
        descuento_porcentaje: producto.descuento_sugerido
      }]);
    }
  };

  // Actualizar cantidad en carrito
  const updateQuantity = (productId: number, delta: number) => {
    setCart(cart.map(item => {
      if (item.producto.id_producto === productId) {
        const newQuantity = item.cantidad + delta;
        if (newQuantity > 0 && newQuantity <= item.producto.stock_actual) {
          return { ...item, cantidad: newQuantity };
        }
      }
      return item;
    }));
  };

  // Actualizar descuento
  const updateDiscount = (productId: number, descuento: number) => {
    setCart(cart.map(item =>
      item.producto.id_producto === productId
        ? { ...item, descuento_porcentaje: Math.min(100, Math.max(0, descuento)) }
        : item
    ));
  };

  // Eliminar del carrito
  const removeFromCart = (productId: number) => {
    setCart(cart.filter(item => item.producto.id_producto !== productId));
  };

  // Limpiar carrito
  const clearCart = () => {
    setCart([]);
    setObservaciones("");
    setSuccess(null);
  };

  // Calcular subtotal de item
  const getItemSubtotal = (item: CartItem) => {
    const subtotal = item.cantidad * item.precio_unitario;
    const descuento = subtotal * (item.descuento_porcentaje / 100);
    return subtotal - descuento;
  };

  // Calcular total
  const getTotal = () => {
    return cart.reduce((total, item) => total + getItemSubtotal(item), 0);
  };

  // Procesar venta
  const procesarVenta = async () => {
    setProcessing(true);
    setError(null);
    setSuccess(null);

    try {
      const requestBody = {
        items: cart.map(item => ({
          id_producto: item.producto.id_producto,
          cantidad: item.cantidad,
          precio_unitario: item.precio_unitario,
          descuento_porcentaje: item.descuento_porcentaje
        })),
        metodo_pago: metodoPago,
        observaciones: observaciones || null
      };

      const response = await fetch(`${API_BASE_URL}/v1/ventas/registrar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        setLastVenta(data.data || data);
        setSuccess(`Venta registrada exitosamente: ${data.data?.numero_venta || 'OK'}`);
        clearCart();
        fetchProductos(); // Refrescar stock
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar la venta');
      }
    } catch (err: any) {
      setError(err.message || 'Error al procesar la venta');
    } finally {
      setProcessing(false);
      setShowConfirmDialog(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Cargando productos...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Punto de Venta</h2>
          <p className="text-muted-foreground">Registra ventas y descuenta stock automáticamente</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchProductos} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {/* Mensajes */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-600">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-600">{success}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Productos disponibles */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Package className="h-5 w-5 mr-2" />
                Productos Disponibles
              </CardTitle>
              <div className="mt-2">
                <Input
                  placeholder="Buscar por nombre o código..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px]">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {filteredProductos.length === 0 ? (
                    <p className="col-span-full text-center text-muted-foreground py-8">
                      No hay productos disponibles
                    </p>
                  ) : (
                    filteredProductos.map((producto) => (
                      <Card
                        key={producto.id_producto}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          producto.stock_actual === 0 ? 'opacity-50' : ''
                        } ${producto.descuento_sugerido > 0 ? 'border-orange-200 bg-orange-50' : ''}`}
                        onClick={() => producto.stock_actual > 0 && addToCart(producto)}
                      >
                        <CardContent className="p-3">
                          <div className="space-y-1">
                            <div className="flex justify-between items-start">
                              <span className="font-medium text-sm truncate">{producto.nombre}</span>
                              {producto.descuento_sugerido > 0 && (
                                <Badge variant="secondary" className="ml-1 text-xs bg-orange-100">
                                  <Tag className="h-3 w-3 mr-1" />
                                  -{producto.descuento_sugerido}%
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-muted-foreground">{producto.codigo_producto}</div>
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-green-600">S/ {Number(producto.precio_venta).toFixed(2)}</span>
                              <Badge variant={producto.stock_actual > 5 ? "default" : "destructive"}>
                                Stock: {Number(producto.stock_actual).toFixed(0)}
                              </Badge>
                            </div>
                            {producto.dias_desde_produccion !== undefined && producto.dias_desde_produccion > 0 && (
                              <div className="text-xs text-orange-600">
                                Producido hace {producto.dias_desde_produccion} día(s)
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Carrito */}
        <div>
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle className="flex items-center">
                <ShoppingCart className="h-5 w-5 mr-2" />
                Carrito ({cart.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {cart.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  Selecciona productos para agregar
                </p>
              ) : (
                <ScrollArea className="h-[300px]">
                  <div className="space-y-3">
                    {cart.map((item) => (
                      <div key={item.producto.id_producto} className="border rounded-lg p-3 space-y-2">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium text-sm">{item.producto.nombre}</p>
                            <p className="text-xs text-muted-foreground">
                              S/ {Number(item.precio_unitario).toFixed(2)} c/u
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => removeFromCart(item.producto.id_producto)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => updateQuantity(item.producto.id_producto, -1)}
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <span className="w-8 text-center font-medium">{item.cantidad}</span>
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => updateQuantity(item.producto.id_producto, 1)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <Input
                              type="number"
                              className="w-14 h-7 text-xs"
                              value={item.descuento_porcentaje}
                              onChange={(e) => updateDiscount(item.producto.id_producto, Number(e.target.value))}
                              min={0}
                              max={100}
                            />
                            <span className="text-xs">%</span>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="font-bold text-green-600">
                            S/ {getItemSubtotal(item).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>

            {cart.length > 0 && (
              <>
                <Separator />
                <CardContent className="pt-4 space-y-4">
                  <div className="space-y-2">
                    <Label>Método de Pago</Label>
                    <Select value={metodoPago} onValueChange={setMetodoPago}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="efectivo">
                          <div className="flex items-center">
                            <Banknote className="h-4 w-4 mr-2" />
                            Efectivo
                          </div>
                        </SelectItem>
                        <SelectItem value="tarjeta">
                          <div className="flex items-center">
                            <CreditCard className="h-4 w-4 mr-2" />
                            Tarjeta
                          </div>
                        </SelectItem>
                        <SelectItem value="transferencia">
                          <div className="flex items-center">
                            <ArrowLeftRight className="h-4 w-4 mr-2" />
                            Transferencia
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Observaciones (opcional)</Label>
                    <Textarea
                      placeholder="Notas de la venta..."
                      value={observaciones}
                      onChange={(e) => setObservaciones(e.target.value)}
                      rows={2}
                    />
                  </div>

                  <Separator />

                  <div className="flex justify-between items-center text-lg font-bold">
                    <span>TOTAL:</span>
                    <span className="text-green-600">S/ {getTotal().toFixed(2)}</span>
                  </div>
                </CardContent>

                <CardFooter className="flex gap-2">
                  <Button variant="outline" className="flex-1" onClick={clearCart}>
                    Limpiar
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={() => setShowConfirmDialog(true)}
                    disabled={processing}
                  >
                    {processing ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <CheckCircle className="h-4 w-4 mr-2" />
                    )}
                    Cobrar
                  </Button>
                </CardFooter>
              </>
            )}
          </Card>
        </div>
      </div>

      {/* Dialog de confirmación */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Venta</DialogTitle>
            <DialogDescription>
              ¿Confirmas el registro de esta venta?
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Productos:</span>
              <span>{cart.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Items totales:</span>
              <span>{cart.reduce((sum, item) => sum + item.cantidad, 0)}</span>
            </div>
            <div className="flex justify-between">
              <span>Método de pago:</span>
              <span className="capitalize">{metodoPago}</span>
            </div>
            <Separator />
            <div className="flex justify-between text-lg font-bold">
              <span>TOTAL:</span>
              <span className="text-green-600">S/ {getTotal().toFixed(2)}</span>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={procesarVenta} disabled={processing}>
              {processing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <CheckCircle className="h-4 w-4 mr-2" />
              )}
              Confirmar Venta
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
