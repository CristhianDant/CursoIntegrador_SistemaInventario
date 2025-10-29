
import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "./ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Separator } from "./ui/separator";
import { Plus, Search, MoreHorizontal, Trash2, Edit } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";
import { API_BASE_URL } from '../constants';

// --- CONFIGURACIÓN DE URL UNIFICADA ---
const ORDEN_COMPRA_API_URL = `${API_BASE_URL}/v1/ordenes-compra`;

// *** INTERFACES AJUSTADAS AL MODELO DE LA API ***

interface OrdenDeCompraDetalle {
  id_orden_detalle?: number;
  id_orden?: number;
  id_insumo: number;
  cantidad: number;
  precio_unitario: number;
  descuento_unitario?: number;
  sub_total: number;
  observaciones?: string;

  // Campos de UI
  nombre_insumo?: string;
}

interface OrdenDeCompra {
  id_orden: number;
  numero_orden: string;
  id_proveedor: number;
  fecha_orden: string;
  fecha_entrega_esperada: string;
  moneda: string;
  tipo_cambio?: number;
  sub_total: number;
  descuento?: number;
  igv: number;
  total: number;
  estado: 'PENDIENTE' | 'APROBADO' | 'RECHAZADO' | 'COMPLETADO' | 'CANCELADO';
  observaciones?: string;
  id_user_creador: number;
  id_user_aprobador?: number;
  fecha_aprobacion?: string;
  anulado?: boolean;
  detalles: OrdenDeCompraDetalle[];

  // Campos de UI
  nombre_proveedor?: string;
  nombre_user_creador?: string;
}

// Datos de ejemplo (reemplazar con llamadas a la API)
const availableSuppliers = [
    { id: 1, name: "Proveedor de Harinas S.A." },
    { id: 2, name: "Distribuidora de Lácteos del Norte" },
    { id: 3, name: "Importadora de Chocolates Belgas" },
];

const availableIngredients = [
    { id: 1, name: "Harina de trigo", unit: "kg", costPerUnit: 1.2 },
    { id: 2, name: "Azúcar refinada", unit: "kg", costPerUnit: 2.5 },
    { id: 3, name: "Huevos frescos", unit: "unidades", costPerUnit: 0.33 },
    { id: 4, name: "Mantequilla", unit: "kg", costPerUnit: 8.5 },
];

export function PurchaseOrderManager() {
  const [orders, setOrders] = useState<OrdenDeCompra[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<OrdenDeCompra | null>(null);
  
  const [formData, setFormData] = useState<Partial<OrdenDeCompra>>({
    detalles: [],
    moneda: 'PEN',
    estado: 'PENDIENTE',
    id_user_creador: 1, // Simulado
  });

  const mapApiToUi = (apiOrder: any): OrdenDeCompra => {
    const supplier = availableSuppliers.find(s => s.id === apiOrder.id_proveedor);
    return {
        ...apiOrder,
        id_orden: apiOrder.id_orden,
        fecha_orden: new Date(apiOrder.fecha_orden).toLocaleDateString(),
        fecha_entrega_esperada: new Date(apiOrder.fecha_entrega_esperada).toLocaleDateString(),
        nombre_proveedor: supplier?.name || 'Desconocido',
        nombre_user_creador: `Usuario ${apiOrder.id_user_creador}`,
        detalles: (apiOrder.detalles || []).map((detail: any) => {
            const ingredient = availableIngredients.find(i => i.id === detail.id_insumo);
            return {
                ...detail,
                nombre_insumo: ingredient?.name || 'Insumo no encontrado',
            };
        }),
    };
  };

  const fetchOrders = async () => {
    try {
        const response = await fetch(ORDEN_COMPRA_API_URL, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) throw new Error('Error al cargar las órdenes de compra');
        
        const rawData = await response.json();
        const mappedOrders: OrdenDeCompra[] = (rawData.data || rawData || []).map(mapApiToUi);
        setOrders(mappedOrders);
    } catch (error) {
        console.error("Error fetching orders:", error);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const calculateTotals = (details: OrdenDeCompraDetalle[] = []) => {
    const subTotal = details.reduce((acc, item) => acc + item.sub_total, 0);
    const igv = subTotal * 0.18; // Asumiendo 18% de IGV
    const total = subTotal + igv;
    return { subTotal, igv, total };
  };

  const handleDetailChange = (index: number, field: keyof OrdenDeCompraDetalle, value: any) => {
    const newDetails = [...(formData.detalles || [])];
    const detail = { ...newDetails[index] };

    if (field === 'id_insumo') {
        const selectedIngredient = availableIngredients.find(ing => ing.id === parseInt(value));
        if (selectedIngredient) {
            detail.id_insumo = selectedIngredient.id;
            detail.precio_unitario = selectedIngredient.costPerUnit;
            detail.nombre_insumo = selectedIngredient.name;
        }
    } else {
        (detail as any)[field] = value;
    }

    if (field === 'cantidad' || field === 'precio_unitario') {
        const cantidad = parseFloat(String(detail.cantidad)) || 0;
        const precio = parseFloat(String(detail.precio_unitario)) || 0;
        detail.sub_total = cantidad * precio;
    }
    
    newDetails[index] = detail;
    const { subTotal, igv, total } = calculateTotals(newDetails);

    setFormData(prev => ({ 
        ...prev, 
        detalles: newDetails,
        sub_total: subTotal,
        igv: igv,
        total: total,
    }));
  };

  const addDetail = () => {
    const newDetail: OrdenDeCompraDetalle = {
      id_insumo: 0,
      cantidad: 0,
      precio_unitario: 0,
      sub_total: 0,
      nombre_insumo: 'Seleccionar insumo'
    };
    setFormData(prev => ({
      ...prev,
      detalles: [...(prev.detalles || []), newDetail]
    }));
  };

  const removeDetail = (index: number) => {
    const newDetails = [...(formData.detalles || [])];
    newDetails.splice(index, 1);
    const { subTotal, igv, total } = calculateTotals(newDetails);
    setFormData(prev => ({ 
        ...prev, 
        detalles: newDetails,
        sub_total: subTotal,
        igv: igv,
        total: total,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingOrder ? `${ORDEN_COMPRA_API_URL}/${editingOrder.id_orden}` : ORDEN_COMPRA_API_URL;
    const method = editingOrder ? 'PUT' : 'POST';

    // Formatear fechas a ISO string para el backend
    const bodyData = {
        ...formData,
        fecha_orden: new Date().toISOString(),
        fecha_entrega_esperada: formData.fecha_entrega_esperada ? new Date(formData.fecha_entrega_esperada).toISOString() : new Date().toISOString(),
    };

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyData),
        });

        if (!response.ok) {
            const errorResult = await response.json();
            throw new Error(errorResult.message || `Error al ${editingOrder ? 'actualizar' : 'crear'} la orden.`);
        }
        
        await fetchOrders();
        setIsDialogOpen(false);
        setEditingOrder(null);
    } catch (error) {
        console.error(`Error during ${method} operation:`, error);
        alert(`Operación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const handleEdit = (order: OrdenDeCompra) => {
    setEditingOrder(order);
    setFormData({
        ...order,
        // Asegurarse de que las fechas estén en formato YYYY-MM-DD para el input
        fecha_orden: new Date(order.fecha_orden).toISOString().split('T')[0],
        fecha_entrega_esperada: new Date(order.fecha_entrega_esperada).toISOString().split('T')[0],
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm("¿Está seguro que desea anular esta orden de compra?")) {
        try {
            const response = await fetch(`${ORDEN_COMPRA_API_URL}/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Error al anular la orden');
            await fetchOrders();
        } catch (error) {
            console.error("Error deleting order:", error);
            alert(`Anulación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
        }
    }
  };

  const openAddDialog = () => {
    setEditingOrder(null);
    setFormData({
      detalles: [],
      numero_orden: `OC-${Date.now().toString().slice(-6)}`,
      id_proveedor: 0,
      fecha_orden: new Date().toISOString().split('T')[0],
      fecha_entrega_esperada: new Date().toISOString().split('T')[0],
      moneda: 'PEN',
      sub_total: 0,
      igv: 0,
      total: 0,
      estado: 'PENDIENTE',
      id_user_creador: 1, // Simulado
    });
    setIsDialogOpen(true);
  };

  const filteredOrders = orders.filter(order =>
    order.numero_orden.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (order.nombre_proveedor || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Órdenes de Compra</h2>
          <p className="text-muted-foreground">Gestiona las órdenes de compra a proveedores.</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Nueva Orden
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingOrder ? "Editar Orden de Compra" : "Nueva Orden de Compra"}</DialogTitle>
              <DialogDescription>
                {editingOrder ? "Modifica los detalles de la orden." : "Crea una nueva orden para un proveedor."}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Encabezado de la orden */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="numero_orden">Número de Orden</Label>
                  <Input id="numero_orden" value={formData.numero_orden || ""} disabled />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="id_proveedor">Proveedor</Label>
                  <Select
                    value={String(formData.id_proveedor || 0)}
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, id_proveedor: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar proveedor" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableSuppliers.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fecha_entrega_esperada">Fecha de Entrega</Label>
                  <Input
                    id="fecha_entrega_esperada"
                    type="date"
                    value={formData.fecha_entrega_esperada || ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ ...prev, fecha_entrega_esperada: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="moneda">Moneda</Label>
                  <Select
                    value={formData.moneda}
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, moneda: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="PEN">Soles (PEN)</SelectItem>
                      <SelectItem value="USD">Dólares (USD)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <Separator />

              {/* Detalles de la orden */}
              <h3 className="text-lg font-semibold">Detalles de la Orden</h3>
              <div className="space-y-4">
                {formData.detalles?.map((detail, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 items-center">
                    <div className="col-span-4">
                      <Select
                        value={String(detail.id_insumo)}
                        onValueChange={(value: string) => handleDetailChange(index, 'id_insumo', value)}
                      >
                        <SelectTrigger><SelectValue placeholder="Insumo" /></SelectTrigger>
                        <SelectContent>
                          {availableIngredients.map(i => <SelectItem key={i.id} value={String(i.id)}>{i.name}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        placeholder="Cantidad"
                        value={detail.cantidad}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'cantidad', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Input
                        type="number"
                        placeholder="Precio U."
                        value={detail.precio_unitario}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'precio_unitario', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Input type="number" placeholder="Subtotal" value={detail.sub_total.toFixed(2)} readOnly />
                    </div>
                    <div className="col-span-2 flex justify-end">
                      <Button variant="ghost" size="icon" onClick={() => removeDetail(index)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}
                <Button type="button" variant="outline" onClick={addDetail}>
                  <Plus className="h-4 w-4 mr-2" /> Añadir Insumo
                </Button>
              </div>

              <Separator />

              {/* Totales y observaciones */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="observaciones">Observaciones</Label>
                  <Textarea
                    id="observaciones"
                    value={formData.observaciones || ""}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData(prev => ({ ...prev, observaciones: e.target.value }))}
                  />
                </div>
                <div className="space-y-2 text-right">
                  <p>Subtotal: {formData.moneda} {formData.sub_total?.toFixed(2)}</p>
                  <p>IGV (18%): {formData.moneda} {formData.igv?.toFixed(2)}</p>
                  <p className="font-bold text-lg">Total: {formData.moneda} {formData.total?.toFixed(2)}</p>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
                <Button type="submit">{editingOrder ? "Guardar Cambios" : "Crear Orden"}</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por número de orden o proveedor..."
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredOrders.map((order) => (
          <Card key={order.id_orden} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{order.numero_orden}</CardTitle>
                  <CardDescription>{order.nombre_proveedor}</CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleEdit(order)}><Edit className="mr-2 h-4 w-4" />Editar</DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleDelete(order.id_orden)} className="text-red-600"><Trash2 className="mr-2 h-4 w-4" />Anular</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm"><strong>Total:</strong> {order.moneda} {order.total.toFixed(2)}</p>
              <p className="text-sm"><strong>Estado:</strong> <span className={`font-semibold ${order.estado === 'APROBADO' ? 'text-green-600' : 'text-yellow-600'}`}>{order.estado}</span></p>
              <p className="text-sm text-muted-foreground">Entrega: {order.fecha_entrega_esperada}</p>
              <p className="text-sm text-muted-foreground">Creado por: {order.nombre_user_creador}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
