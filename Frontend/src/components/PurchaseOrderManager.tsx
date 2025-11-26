
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
const ORDEN_COMPRA_API_URL = `${API_BASE_URL}/v1/ordenes_compra`;

// *** INTERFACES AJUSTADAS AL MODELO DE LA API ***

interface Supplier {
  id_proveedor?: number;
  id?: number;
  nombre_proveedor?: string;
  nombre?: string;
  name?: string;
}

interface Insumo {
  id_insumo?: number;
  id?: number;
  nombre_insumo?: string;
  nombre?: string;
  name?: string;
  precio_promedio?: number;
  unidad_medida?: string;
  unit?: string;
}

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
  estado: 'PENDIENTE' | 'TERMINADO' | 'ANULADO' | 'ACTIVA' | 'REGISTRADO' | 'COMPLETADO';
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
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [insumos, setInsumos] = useState<Insumo[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<OrdenDeCompra | null>(null);
  const [loading, setLoading] = useState(true);
  const [isViewInsumosOpen, setIsViewInsumosOpen] = useState(false);
  const [selectedOrderForInsumos, setSelectedOrderForInsumos] = useState<OrdenDeCompra | null>(null);
  
  const [formData, setFormData] = useState<Partial<OrdenDeCompra>>({
    detalles: [],
    moneda: 'PEN',
    estado: 'PENDIENTE',
    id_user_creador: 1, // Simulado
  });

  const loadAllData = async () => {
    try {
      const [suppliersRes, insumosRes, ordersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/v1/proveedores`),
        fetch(`${API_BASE_URL}/v1/insumos`),
        fetch(ORDEN_COMPRA_API_URL),
      ]);

      if (suppliersRes.ok) {
        const suppliersData = await suppliersRes.json();
        const suppliersList = Array.isArray(suppliersData) ? suppliersData : (suppliersData.data || []);
        setSuppliers(suppliersList);
      } else {
        setSuppliers([]);
      }

      if (insumosRes.ok) {
        const insumosData = await insumosRes.json();
        const insumosList = Array.isArray(insumosData) ? insumosData : (insumosData.data || []);
        setInsumos(insumosList);
      } else {
        setInsumos([]);
      }

      if (ordersRes.ok) {
        const ordersData = await ordersRes.json();
        const ordersList = Array.isArray(ordersData) ? ordersData : (ordersData.data || []);
        const mappedOrders = ordersList.map(mapApiToUi);
        setOrders(mappedOrders);
      } else {
        setOrders([]);
      }
    } catch (error) {
      console.error("Error loading data:", error);
      setSuppliers([]);
      setInsumos([]);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const mapApiToUi = (apiOrder: any): OrdenDeCompra => {
    const supplier = suppliers.find(s => (s.id_proveedor || s.id) === apiOrder.id_proveedor);
    return {
        ...apiOrder,
        id_orden: apiOrder.id_orden,
        fecha_orden: new Date(apiOrder.fecha_orden).toLocaleDateString(),
        fecha_entrega_esperada: new Date(apiOrder.fecha_entrega_esperada).toLocaleDateString(),
        nombre_proveedor: supplier?.nombre_proveedor || supplier?.nombre || supplier?.name || 'Desconocido',
        nombre_user_creador: `Usuario ${apiOrder.id_user_creador}`,
        detalles: (apiOrder.detalles || []).map((detail: any) => {
            const ingredient = insumos.find(i => (i.id_insumo || i.id) === detail.id_insumo);
            return {
                ...detail,
                nombre_insumo: ingredient?.nombre_insumo || ingredient?.nombre || ingredient?.name || 'Insumo no encontrado',
            };
        }),
    };
  };

  useEffect(() => {
    loadAllData();
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
    
    // Validar que se haya seleccionado un proveedor
    if (!formData.id_proveedor || formData.id_proveedor === 0) {
      alert('Por favor selecciona un proveedor antes de continuar.');
      return;
    }

    // En creación, validar que la fecha de entrega esté completa
    // En edición, mantener la fecha existente si está vacía
    if (!editingOrder && !formData.fecha_entrega_esperada) {
      alert('Por favor selecciona una fecha de entrega esperada.');
      return;
    }

    // Función para convertir fecha de YYYY-MM-DD a ISO datetime
    const convertDateToBackendFormat = (date: string | undefined): string | undefined => {
      if (!date) return undefined;
      // Si ya está en formato DD/MM/YYYY, convertir a ISO
      if (/^\d{2}\/\d{2}\/\d{4}/.test(date)) {
        const [day, month, year] = date.split('/');
        return `${year}-${month}-${day}T00:00:00`;
      }
      // Si está en formato YYYY-MM-DD, convertir a ISO con hora
      if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return `${date}T00:00:00`;
      }
      // Si ya tiene hora (ISO), devolverlo tal cual
      if (/^\d{4}-\d{2}-\d{2}T/.test(date)) {
        return date;
      }
      return date;
    };

    // Función para detectar si los detalles fueron modificados
    const haveDetailsChanged = (): boolean => {
      if (!editingOrder) return true; // En creación siempre hay cambios
      
      const originalDetails = editingOrder.detalles || [];
      const currentDetails = formData.detalles || [];
      
      // Si el número de detalles cambió
      if (originalDetails.length !== currentDetails.length) {
        console.log(`Número de detalles cambió: ${originalDetails.length} -> ${currentDetails.length}`);
        return true;
      }
      
      // Función auxiliar para comparar números con tolerancia
      const numbersEqual = (a: number | undefined, b: number | undefined, tolerance = 0.01): boolean => {
        const aVal = parseFloat(String(a || 0));
        const bVal = parseFloat(String(b || 0));
        return Math.abs(aVal - bVal) < tolerance;
      };
      
      // Comparar cada detalle
      for (let i = 0; i < originalDetails.length; i++) {
        const orig = originalDetails[i];
        const curr = currentDetails[i];
        
        if (
          orig.id_insumo !== curr.id_insumo ||
          !numbersEqual(orig.cantidad, curr.cantidad) ||
          !numbersEqual(orig.precio_unitario, curr.precio_unitario) ||
          !numbersEqual(orig.descuento_unitario, curr.descuento_unitario) ||
          !numbersEqual(orig.sub_total, curr.sub_total)
        ) {
          console.log(`Detalle ${i} cambió:`, {
            insumo: `${orig.id_insumo} -> ${curr.id_insumo}`,
            cantidad: `${orig.cantidad} -> ${curr.cantidad}`,
            precio: `${orig.precio_unitario} -> ${curr.precio_unitario}`,
            descuento: `${orig.descuento_unitario} -> ${curr.descuento_unitario}`,
            subtotal: `${orig.sub_total} -> ${curr.sub_total}`
          });
          return true;
        }
      }
      
      return false;
    };

    // Si estamos editando y la fecha está vacía, usar la fecha existente
    let fechaEntrega = formData.fecha_entrega_esperada || (editingOrder?.fecha_entrega_esperada || '');
    // Convertir a formato que espera el backend
    fechaEntrega = convertDateToBackendFormat(fechaEntrega) || '';
    
    const url = editingOrder ? `${ORDEN_COMPRA_API_URL}/${editingOrder.id_orden}` : ORDEN_COMPRA_API_URL;
    const method = editingOrder ? 'PUT' : 'POST';

    try {
        // Construir objeto de datos limpio
        const bodyData: any = {
            numero_orden: formData.numero_orden,
            id_proveedor: formData.id_proveedor,
            fecha_entrega_esperada: fechaEntrega,
            moneda: formData.moneda || 'PEN',
            tipo_cambio: formData.tipo_cambio || 1,
            sub_total: parseFloat(String(formData.sub_total || 0)),
            descuento: formData.descuento ? parseFloat(String(formData.descuento)) : 0,
            igv: parseFloat(String(formData.igv || 0)),
            total: parseFloat(String(formData.total || 0)),
            estado: formData.estado || 'PENDIENTE',
            observaciones: formData.observaciones || null,
            id_user_creador: formData.id_user_creador || 1,
        };

        // Agregar detalles si:
        // 1. Es creación (POST) - siempre agregar
        // 2. Es edición (PUT) Y los detalles fueron modificados
        const detailsChanged = editingOrder && haveDetailsChanged();
        if (!editingOrder || detailsChanged) {
            console.log(`Detalles ${detailsChanged ? 'MODIFICADOS' : 'sin cambios'} - incluyendo en petición`);
            bodyData.detalles = (formData.detalles || []).map(d => ({
                id_insumo: d.id_insumo,
                cantidad: parseFloat(String(d.cantidad || 0)),
                precio_unitario: parseFloat(String(d.precio_unitario || 0)),
                descuento_unitario: d.descuento_unitario ? parseFloat(String(d.descuento_unitario)) : 0,
                sub_total: parseFloat(String(d.sub_total || 0)),
                observaciones: d.observaciones || null,
                // NO incluir id_orden_detalle - el backend lo maneja al recrear
            }));
        } else {
            console.log('Detalles sin cambios - NO incluyendo en petición (se preservarán en backend)');
        }

        console.log('Enviando datos:', JSON.stringify(bodyData, null, 2));

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyData),
        });

        let errorMsg = '';
        const responseData = await response.json().catch(() => null);

        if (!response.ok) {
            if (responseData) {
                // Intentar extraer el mensaje de error del backend
                if (typeof responseData === 'string') {
                    errorMsg = responseData;
                } else if (responseData.detail) {
                    errorMsg = Array.isArray(responseData.detail) 
                        ? responseData.detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join(', ')
                        : String(responseData.detail);
                } else if (responseData.message) {
                    errorMsg = responseData.message;
                } else {
                    errorMsg = JSON.stringify(responseData);
                }
            }
            throw new Error(errorMsg || `Error al ${editingOrder ? 'actualizar' : 'crear'} la orden.`);
        }
        
        console.log('Respuesta del servidor:', JSON.stringify(responseData, null, 2));
        
        // Si es creación (POST), obtener la orden completa incluyendo detalles
        if (!editingOrder && responseData && responseData.id_orden) {
            try {
                const detailedOrderRes = await fetch(`${ORDEN_COMPRA_API_URL}/${responseData.id_orden}`);
                if (detailedOrderRes.ok) {
                    const detailedOrder = await detailedOrderRes.json();
                    console.log('Orden detallada obtenida:', JSON.stringify(detailedOrder, null, 2));
                    
                    // Procesar la respuesta del backend (puede ser directa o envuelta en 'data')
                    let orderToAdd = detailedOrder;
                    if (detailedOrder && detailedOrder.data) {
                        orderToAdd = detailedOrder.data;
                    } else if (detailedOrder && typeof detailedOrder === 'string') {
                        orderToAdd = JSON.parse(detailedOrder);
                    }
                    
                    const mappedOrder = mapApiToUi(orderToAdd);
                    console.log('Orden mapeada:', JSON.stringify(mappedOrder, null, 2));
                    
                    setOrders(prev => [mappedOrder, ...prev]);
                } else {
                    // Si no puede obtener detalles, al menos recargar todo
                    await loadAllData();
                }
            } catch (error) {
                console.error('Error obteniendo detalles de la orden:', error);
                // Si hay error obteniendo detalles, recargar todo
                await loadAllData();
            }
        } else {
            // Para edición o si algo falla, recargar todo
            await loadAllData();
        }
        
        setIsDialogOpen(false);
        setEditingOrder(null);
        alert(`Orden ${editingOrder ? 'actualizada' : 'creada'} exitosamente`);
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`Error during ${method} operation:`, errorMessage);
        alert(`Operación fallida: ${errorMessage}`);
    }
  };

  const handleEdit = (order: OrdenDeCompra) => {
    // Función helper para convertir fecha a formato YYYY-MM-DD
    const formatDateForInput = (dateValue: string | Date | undefined): string => {
      if (!dateValue) return '';
      
      const dateStr = String(dateValue).trim();
      
      // Si ya está en formato YYYY-MM-DD, devolverlo como está
      if (/^\d{4}-\d{2}-\d{2}/.test(dateStr)) {
        return dateStr.split('T')[0];
      }
      
      // Si está en formato DD/MM/YYYY, convertir a YYYY-MM-DD
      if (/^\d{2}\/\d{2}\/\d{4}/.test(dateStr)) {
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month}-${day}`;
      }
      
      // Intentar crear una fecha válida
      try {
        const date = typeof dateValue === 'string' ? new Date(dateValue) : dateValue;
        if (isNaN(date.getTime())) {
          console.warn('Fecha inválida:', dateValue);
          return '';
        }
        return date.toISOString().split('T')[0];
      } catch (error) {
        console.warn('Error al parsear fecha:', dateValue, error);
        return '';
      }
    };

    console.log('Orden a editar:', order);
    console.log('Fecha orden original:', order.fecha_orden);
    console.log('Fecha entrega esperada original:', order.fecha_entrega_esperada);

    setEditingOrder(order);
    setFormData({
        ...order,
        // Asegurarse de que las fechas estén en formato YYYY-MM-DD para el input
        fecha_orden: formatDateForInput(order.fecha_orden),
        fecha_entrega_esperada: formatDateForInput(order.fecha_entrega_esperada),
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm("¿Está seguro que desea anular esta orden de compra?")) {
        try {
            const response = await fetch(`${ORDEN_COMPRA_API_URL}/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Error al anular la orden');
            await loadAllData();
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
        <Button onClick={openAddDialog}>
          <Plus className="h-4 w-4 mr-2" />
          Nueva Orden
        </Button>
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingOrder ? "Editar Orden de Compra" : "Nueva Orden de Compra"}</DialogTitle>
              <DialogDescription>
                {editingOrder ? "Modifica los detalles y estado de la orden." : "Crea una nueva orden para un proveedor."}
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit}>
              {/* Encabezado de la orden */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="numero_orden">Número de Orden</Label>
                  <Input
                    id="numero_orden"
                    value={formData.numero_orden || ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ ...prev, numero_orden: e.target.value }))}
                    disabled={!!editingOrder}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="id_proveedor">Proveedor</Label>
                  <Select
                    value={String(formData.id_proveedor || 0)}
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, id_proveedor: parseInt(value) }))}
                    disabled={!!editingOrder}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar proveedor" />
                    </SelectTrigger>
                    <SelectContent>
                      {suppliers.map(p => <SelectItem key={p.id_proveedor || p.id} value={String(p.id_proveedor || p.id)}>{p.nombre_proveedor || p.nombre || p.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fecha_orden">Fecha de Orden</Label>
                  <Input
                    id="fecha_orden"
                    type="date"
                    value={formData.fecha_orden || ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ ...prev, fecha_orden: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fecha_entrega_esperada">Fecha de Entrega Esperada</Label>
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
                    value={formData.moneda || 'PEN'}
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

                <div className="space-y-2">
                  <Label htmlFor="estado">Estado</Label>
                  <Select
                    value={String(formData.estado || 'PENDIENTE')}
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, estado: value as OrdenDeCompra['estado'] }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="PENDIENTE">Pendiente</SelectItem>
                      <SelectItem value="ACTIVA">Activa</SelectItem>
                      <SelectItem value="REGISTRADO">Registrado</SelectItem>
                      <SelectItem value="TERMINADO">Terminado</SelectItem>
                      <SelectItem value="COMPLETADO">Completado</SelectItem>
                      <SelectItem value="ANULADO">Anulado</SelectItem>
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
                    <div className="col-span-12 md:col-span-4">
                      <label className="text-xs text-muted-foreground md:hidden">Insumo</label>
                      <Select
                        value={String(detail.id_insumo)}
                        onValueChange={(value: string) => handleDetailChange(index, 'id_insumo', value)}
                      >
                        <SelectTrigger><SelectValue placeholder="Insumo" /></SelectTrigger>
                        <SelectContent>
                          {insumos.map(i => <SelectItem key={i.id_insumo || i.id} value={String(i.id_insumo || i.id)}>{i.nombre_insumo || i.nombre || i.name}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-6 md:col-span-2">
                      <label className="text-xs text-muted-foreground md:hidden">Cantidad</label>
                      <Input
                        type="number"
                        placeholder="Cantidad"
                        value={detail.cantidad}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'cantidad', e.target.value)}
                      />
                    </div>
                    <div className="col-span-6 md:col-span-2">
                      <label className="text-xs text-muted-foreground md:hidden">Precio Unit.</label>
                      <Input
                        type="number"
                        placeholder="Precio U."
                        value={detail.precio_unitario}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'precio_unitario', e.target.value)}
                      />
                    </div>
                    <div className="col-span-6 md:col-span-2">
                      <label className="text-xs text-muted-foreground md:hidden">Subtotal</label>
                      <Input type="number" placeholder="Subtotal" value={detail.sub_total.toFixed(2)} readOnly />
                    </div>
                    <div className="col-span-6 md:col-span-2 flex justify-end">
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="observaciones">Observaciones</Label>
                  <Textarea
                    id="observaciones"
                    value={formData.observaciones || ""}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData(prev => ({ ...prev, observaciones: e.target.value }))}
                    className="min-h-24"
                  />
                </div>
                
                <div className="space-y-4">
                  {/* Resumen de totales */}
                  <div className="bg-muted p-4 rounded-lg space-y-2">
                    <h4 className="font-semibold text-sm">Resumen</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Subtotal:</span>
                        <span className="font-medium">{formData.moneda} {formData.sub_total?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>IGV (18%):</span>
                        <span className="font-medium">{formData.moneda} {formData.igv?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-base font-bold border-t pt-2">
                        <span>Total:</span>
                        <span>{formData.moneda} {formData.total?.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Información adicional si es edición */}
                  {editingOrder && (
                    <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg space-y-2 text-sm">
                      <h4 className="font-semibold">Información de la Orden</h4>
                      <div className="space-y-1 text-xs">
                        <p><strong>Creado por:</strong> {editingOrder.nombre_user_creador || 'Usuario'}</p>
                        <p><strong>Creado:</strong> {new Date(editingOrder.fecha_orden).toLocaleDateString()}</p>
                        {editingOrder.fecha_aprobacion && (
                          <p><strong>Aprobado:</strong> {new Date(editingOrder.fecha_aprobacion).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
                <Button type="submit">{editingOrder ? "Guardar Cambios" : "Crear Orden"}</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>

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
                    <DropdownMenuItem onClick={() => { setSelectedOrderForInsumos(order); setIsViewInsumosOpen(true); }}><Search className="mr-2 h-4 w-4" />Ver Insumos</DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleEdit(order)}><Edit className="mr-2 h-4 w-4" />Editar</DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleDelete(order.id_orden)} className="text-red-600"><Trash2 className="mr-2 h-4 w-4" />Anular</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm"><strong>Total:</strong> {order.moneda} {order.total.toFixed(2)}</p>
                  <p className="text-sm"><strong>Estado:</strong> <span className={`font-semibold ${order.estado === 'COMPLETADO' || order.estado === 'TERMINADO' ? 'text-green-600' : order.estado === 'ANULADO' ? 'text-red-600' : 'text-yellow-600'}`}>{order.estado}</span></p>
              <p className="text-sm text-muted-foreground">Entrega: {order.fecha_entrega_esperada}</p>
              <p className="text-sm text-muted-foreground">Creado por: {order.nombre_user_creador}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal para ver insumos de la orden */}
      <Dialog open={isViewInsumosOpen} onOpenChange={setIsViewInsumosOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Insumos de la Orden {selectedOrderForInsumos?.numero_orden}</DialogTitle>
            <DialogDescription>
              Detalles de los insumos incluidos en esta orden de compra
            </DialogDescription>
          </DialogHeader>

          {selectedOrderForInsumos && selectedOrderForInsumos.detalles && selectedOrderForInsumos.detalles.length > 0 ? (
            <div className="space-y-4">
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted border-b">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Insumo</th>
                      <th className="px-4 py-3 text-right font-semibold">Cantidad</th>
                      <th className="px-4 py-3 text-right font-semibold">Precio Unit.</th>
                      <th className="px-4 py-3 text-right font-semibold">Descuento</th>
                      <th className="px-4 py-3 text-right font-semibold">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedOrderForInsumos.detalles.map((detalle, index) => (
                      <tr key={index} className="border-b hover:bg-muted/50">
                        <td className="px-4 py-3">{detalle.nombre_insumo || 'Insumo'}</td>
                        <td className="px-4 py-3 text-right">{detalle.cantidad}</td>
                        <td className="px-4 py-3 text-right">{selectedOrderForInsumos.moneda} {detalle.precio_unitario.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right">{detalle.descuento_unitario ? `${selectedOrderForInsumos.moneda} ${detalle.descuento_unitario.toFixed(2)}` : '-'}</td>
                        <td className="px-4 py-3 text-right font-semibold">{selectedOrderForInsumos.moneda} {detalle.sub_total.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Resumen de totales */}
              <div className="bg-muted p-4 rounded-lg space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span className="font-medium">{selectedOrderForInsumos.moneda} {selectedOrderForInsumos.sub_total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>IGV (18%):</span>
                  <span className="font-medium">{selectedOrderForInsumos.moneda} {selectedOrderForInsumos.igv.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-base font-bold border-t pt-2">
                  <span>Total:</span>
                  <span>{selectedOrderForInsumos.moneda} {selectedOrderForInsumos.total.toFixed(2)}</span>
                </div>
              </div>

              {selectedOrderForInsumos.observaciones && (
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                  <p className="text-sm font-semibold mb-1">Observaciones:</p>
                  <p className="text-sm text-muted-foreground">{selectedOrderForInsumos.observaciones}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">
              No hay insumos registrados en esta orden
            </div>
          )}

          <div className="flex justify-end">
            <Button type="button" variant="ghost" onClick={() => setIsViewInsumosOpen(false)}>Cerrar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
