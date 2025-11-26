import React, { useState, useEffect } from 'react';
import { Plus, Search, MoreVertical, Edit, Trash2, FileText, Calendar, User, Truck, ShoppingCart, Hash, DollarSign, Package } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { API_BASE_URL } from '../constants';

// --- CONFIGURACIÓN DE URL UNIFICADA ---
const SUPPLY_ENTRY_API_URL = `${API_BASE_URL}/v1/ingresos_productos`;

// --- INTERFACES BASADAS EN EL SCHEMA ---
interface SupplyEntryDetail {
  id_ingreso_detalle?: number;
  id_ingreso?: number;
  id_insumo: number;
  cantidad_ordenada: number;
  cantidad_ingresada: number;
  precio_unitario: number;
  subtotal: number;
  fecha_vencimiento?: string;
  // UI fields
  nombre_insumo?: string;
}

interface SupplyEntry {
  id_ingreso: number;
  numero_ingreso: string;
  id_orden_compra: number;
  numero_documento: string;
  tipo_documento: "FACTURA" | "BOLETA" | "GUIA_REMISION";
  fecha_registro: string;
  fecha_ingreso: string;
  fecha_documento: string;
  id_user: number;
  id_proveedor: number;
  observaciones?: string;
  estado: "PENDIENTE" | "COMPLETADO" | "ANULADO";
  monto_total: number;
  anulado: boolean;
  detalles: SupplyEntryDetail[];
  // UI fields
  nombre_proveedor?: string;
}

interface Supplier {
  id_proveedor?: number;
  id?: number;
  nombre_proveedor?: string;
  nombre?: string;
  name?: string;
}

interface PurchaseOrder {
  id_orden?: number;
  id?: number;
  numero_orden?: string;
  number?: string;
}

interface Insumo {
  id_insumo?: number;
  id?: number;
  nombre_insumo?: string;
  nombre?: string;
  name?: string;
  unidad_medida?: string;
  unit?: string;
}

interface PurchaseOrderDetailed {
  id_orden: number;
  numero_orden: string;
  id_proveedor: number;
  detalles: Array<{
    id_insumo: number;
    cantidad: number;
    precio_unitario: number;
    sub_total: number;
  }>;
}

export function SupplyEntryManager() {
  const [entries, setEntries] = useState<SupplyEntry[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrderDetailed[]>([]);
  const [insumos, setInsumos] = useState<Insumo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<SupplyEntry | null>(null);
  
  const [formData, setFormData] = useState<Partial<SupplyEntry>>({
    detalles: [],
    estado: "PENDIENTE",
    tipo_documento: "FACTURA",
  });

  const loadAllData = async (includeArchivedOrders: boolean = false) => {
    console.log('=== INICIANDO loadAllData ===');
    try {
      const [suppliersRes, purchaseOrdersRes, insumosRes, entriesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/v1/proveedores`),
        fetch(`${API_BASE_URL}/v1/ordenes_compra?activas_solo=${!includeArchivedOrders}`),
        fetch(`${API_BASE_URL}/v1/insumos`),
        fetch(SUPPLY_ENTRY_API_URL),
      ]);

      // Parse suppliers
      let suppliersList: Supplier[] = [];
      if (suppliersRes.ok) {
        const suppliersData = await suppliersRes.json();
        suppliersList = Array.isArray(suppliersData) ? suppliersData : (suppliersData.data || []);
        setSuppliers(suppliersList);
      }

      // Parse purchase orders
      let ordersList: PurchaseOrderDetailed[] = [];
      if (purchaseOrdersRes.ok) {
        const ordersData = await purchaseOrdersRes.json();
        console.log('=== ORDENES_COMPRA RAW ===', ordersData);
        ordersList = Array.isArray(ordersData) ? ordersData : (ordersData.data || []);
        console.log('=== ORDENES_COMPRA PARSED ===', ordersList);
        setPurchaseOrders(ordersList);
      } else {
        console.error('Error cargando órdenes de compra:', purchaseOrdersRes.status);
        setPurchaseOrders([]);
      }

      // Parse insumos
      let insumosList: Insumo[] = [];
      if (insumosRes.ok) {
        const insumosData = await insumosRes.json();
        insumosList = Array.isArray(insumosData) ? insumosData : (insumosData.data || []);
        setInsumos(insumosList);
      }

      // Parse entries y mapear con los datos ya cargados
      if (entriesRes.ok) {
        const entriesData = await entriesRes.json();
        const entriesList = Array.isArray(entriesData) ? entriesData : (entriesData.data || []);
        
        // Mapear con los datos que ya tenemos en las variables locales
        const mappedEntries = entriesList.map((entry: any) => {
          const supplier = suppliersList.find(s => (s.id_proveedor || s.id) === entry.id_proveedor);
          return {
            ...entry,
            id_ingreso: entry.id_ingreso,
            nombre_proveedor: supplier?.nombre_proveedor || supplier?.nombre || supplier?.name || 'N/A',
            fecha_ingreso: new Date(entry.fecha_ingreso).toISOString().split('T')[0],
            fecha_documento: new Date(entry.fecha_documento).toISOString().split('T')[0],
            detalles: (entry.detalles || []).map((detail: any) => {
              const insumo = insumosList.find(i => (i.id_insumo || i.id) === detail.id_insumo);
              return {
                ...detail,
                nombre_insumo: insumo?.nombre_insumo || insumo?.nombre || insumo?.name || 'Insumo desconocido',
                fecha_vencimiento: detail.fecha_vencimiento ? new Date(detail.fecha_vencimiento).toISOString().split('T')[0] : undefined,
              };
            }),
          };
        });
        
        setEntries(mappedEntries);
      } else {
        setEntries([]);
      }
    } catch (error) {
      console.error("Error loading data:", error);
      setSuppliers([]);
      setPurchaseOrders([]);
      setInsumos([]);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData(false); // Cargar solo órdenes activas en la lista inicial
  }, []);

  const handleDetailChange = (index: number, field: keyof SupplyEntryDetail, value: any) => {
    const newDetails = [...(formData.detalles || [])];
    const detail = newDetails[index];
    
    let updatedDetail = { ...detail, [field]: value };

    if (field === 'id_insumo') {
        const insumo = insumos.find(i => (i.id_insumo || i.id) === Number(value));
        updatedDetail.nombre_insumo = insumo?.nombre_insumo || insumo?.nombre || insumo?.name;
    }

    if (field === 'cantidad_ingresada' || field === 'precio_unitario') {
        const cantidad = field === 'cantidad_ingresada' ? Number(value) : detail.cantidad_ingresada;
        const precio = field === 'precio_unitario' ? Number(value) : detail.precio_unitario;
        updatedDetail.subtotal = (cantidad || 0) * (precio || 0);
    }
    
    newDetails[index] = updatedDetail;
    const total = newDetails.reduce((acc, d) => acc + (d.subtotal || 0), 0);
    setFormData(prev => ({ ...prev, detalles: newDetails, monto_total: total }));
  };

  const addDetail = () => {
    const newDetail: SupplyEntryDetail = {
      id_insumo: 0,
      cantidad_ordenada: 0,
      cantidad_ingresada: 0,
      precio_unitario: 0,
      subtotal: 0,
    };
    setFormData(prev => ({ ...prev, detalles: [...(prev.detalles || []), newDetail] }));
  };

  const removeDetail = (index: number) => {
    const newDetails = [...(formData.detalles || [])];
    newDetails.splice(index, 1);
    const total = newDetails.reduce((acc, d) => acc + (d.subtotal || 0), 0);
    setFormData(prev => ({ ...prev, detalles: newDetails, monto_total: total }));
  };

  const handleSelectPurchaseOrder = async (orderId: string) => {
    const orden = purchaseOrders.find(o => o.id_orden === Number(orderId));
    
    if (!orden) {
      console.error('Orden de compra no encontrada');
      return;
    }

    // Buscar el proveedor de esta orden
    const proveedor = suppliers.find(s => (s.id_proveedor || s.id) === orden.id_proveedor);
    
    // Mapear los detalles de la orden de compra a detalles de ingreso
    const detallesMapados = (orden.detalles || []).map(detalle => {
      const insumo = insumos.find(i => (i.id_insumo || i.id) === detalle.id_insumo);
      return {
        id_insumo: detalle.id_insumo,
        cantidad_ordenada: detalle.cantidad,
        cantidad_ingresada: detalle.cantidad, // Por defecto, asumimos que llegó todo
        precio_unitario: detalle.precio_unitario,
        subtotal: detalle.sub_total,
        nombre_insumo: insumo?.nombre_insumo || insumo?.nombre || insumo?.name,
      };
    });

    const totalMonto = detallesMapados.reduce((acc, d) => acc + (d.subtotal || 0), 0);

    console.log('Orden seleccionada:', { orden, proveedor, detalles: detallesMapados });

    // Actualizar el formulario con los datos de la orden
    setFormData(prev => ({
      ...prev,
      id_orden_compra: orden.id_orden,
      id_proveedor: orden.id_proveedor,
      detalles: detallesMapados,
      monto_total: totalMonto,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingEntry ? `${SUPPLY_ENTRY_API_URL}/${editingEntry.id_ingreso}` : SUPPLY_ENTRY_API_URL;
    const method = editingEntry ? 'PUT' : 'POST';

    // Asegurarse de que los campos de fecha tengan el formato correcto
    const body = {
        ...formData,
        fecha_ingreso: formData.fecha_ingreso ? new Date(formData.fecha_ingreso).toISOString() : new Date().toISOString(),
        fecha_documento: formData.fecha_documento ? new Date(formData.fecha_documento).toISOString() : new Date().toISOString(),
        id_user: 1, // Hardcodeado por ahora
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Error al guardar el ingreso');
      }
      await loadAllData(false); // Cargar solo órdenes activas después de guardar
      setIsDialogOpen(false);
    } catch (error) {
      console.error("Submit error:", error);
      alert(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const handleEdit = async (entry: SupplyEntry) => {
    console.log('=== EDIT: Entry ===', entry);
    console.log('=== EDIT: id_orden_compra ===', entry.id_orden_compra);
    
    setEditingEntry(entry);
    
    // Si la orden no está en la lista actual (porque está anulada), cargar todas las órdenes
    let ordenCompra = purchaseOrders.find(o => o.id_orden === entry.id_orden_compra);
    if (!ordenCompra && entry.id_orden_compra) {
      console.log('⚠️ ORDEN ANULADA DETECTADA - Recargando con órdenes anuladas');
      await loadAllData(true); // true = incluir órdenes anuladas
      // Buscar de nuevo después de recargar
      ordenCompra = purchaseOrders.find(o => o.id_orden === entry.id_orden_compra);
    }
    
    console.log('=== EDIT: ordenCompra encontrada ===', ordenCompra);
    
    // Mapear correctamente los detalles con los insumos actuales
    const detallesConNombres = (entry.detalles || []).map(detail => {
      const insumo = insumos.find(i => (i.id_insumo || i.id) === detail.id_insumo);
      
      // Si cantidad_ordenada no existe, buscarla en la orden de compra
      let cantidadOrdenada = detail.cantidad_ordenada;
      if (!cantidadOrdenada && ordenCompra) {
        const detalleOrden = ordenCompra.detalles?.find(d => d.id_insumo === detail.id_insumo);
        console.log(`Detalle ${detail.id_insumo} en orden:`, detalleOrden);
        cantidadOrdenada = detalleOrden?.cantidad || detail.cantidad_ingresada || 0;
      }
      
      return {
        ...detail,
        cantidad_ordenada: cantidadOrdenada || 0,
        nombre_insumo: insumo?.nombre_insumo || insumo?.nombre || insumo?.name || detail.nombre_insumo || 'Insumo desconocido'
      };
    });
    
    console.log('=== EDIT: detallesConNombres ===', detallesConNombres);
    
    const supplier = suppliers.find(s => (s.id_proveedor || s.id) === entry.id_proveedor);
    
    setFormData({
      ...entry,
      nombre_proveedor: supplier?.nombre_proveedor || supplier?.nombre || supplier?.name || entry.nombre_proveedor || 'N/A',
      detalles: detallesConNombres
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea anular este ingreso?")) return;
    try {
      // Lógica de anulación (puede ser un PUT o un DELETE)
      const response = await fetch(`${SUPPLY_ENTRY_API_URL}/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Error al anular el ingreso');
      await loadAllData(false); // Cargar solo órdenes activas después de eliminar
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  const openNewDialog = () => {
    setEditingEntry(null);
    setFormData({
      numero_ingreso: `ING-${Date.now().toString().slice(-5)}`,
      detalles: [],
      estado: "PENDIENTE",
      tipo_documento: "FACTURA",
      monto_total: 0,
      fecha_ingreso: new Date().toISOString().split('T')[0],
      fecha_documento: new Date().toISOString().split('T')[0],
    });
    setIsDialogOpen(true);
  };

  const filteredEntries = entries.filter(entry =>
    entry.numero_ingreso.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.numero_documento.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (entry.nombre_proveedor || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Ingreso de Insumos</h2>
          <p className="text-muted-foreground">Registra las entradas de insumos desde proveedores.</p>
        </div>
        <Button onClick={openNewDialog}><Plus className="mr-2 h-4 w-4" /> Nuevo Ingreso</Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por Nº de ingreso, documento o proveedor..."
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEntries.map(entry => (
          <Card key={entry.id_ingreso}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" /> {entry.numero_ingreso}
                  </CardTitle>
                  <CardDescription>{entry.nombre_proveedor}</CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon"><MoreVertical className="h-4 w-4" /></Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleEdit(entry)}><Edit className="mr-2 h-4 w-4" /> Editar</DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleDelete(entry.id_ingreso)} className="text-red-500"><Trash2 className="mr-2 h-4 w-4" /> Anular</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5"><Truck className="h-4 w-4" /> Proveedor</span>
                <span>{entry.nombre_proveedor}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5"><Calendar className="h-4 w-4" /> Fecha Ingreso</span>
                <span>{entry.fecha_ingreso}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5"><DollarSign className="h-4 w-4" /> Monto Total</span>
                <span className="font-semibold">S/ {entry.monto_total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5"><Package className="h-4 w-4" /> Estado</span>
                <Badge variant={entry.estado === 'COMPLETADO' ? 'default' : 'secondary'}>{entry.estado}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingEntry ? 'Editar Ingreso' : 'Nuevo Ingreso'}</DialogTitle>
            <DialogDescription>Completa la información del ingreso de insumos.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="numero_ingreso">Nº Ingreso</Label>
                <Input id="numero_ingreso" value={formData.numero_ingreso || ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(p => ({ ...p, numero_ingreso: e.target.value }))} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="id_orden_compra">Orden de Compra {!editingEntry && '*'}</Label>
                {editingEntry ? (
                  <div className="px-3 py-2 rounded-md border border-input bg-muted text-sm min-h-10 flex items-center">
                    {purchaseOrders.find(o => o.id_orden === formData.id_orden_compra)?.numero_orden || 'N/A'}
                  </div>
                ) : (
                  <Select 
                    onValueChange={(value: string) => handleSelectPurchaseOrder(value)} 
                    value={String(formData.id_orden_compra || '')}
                  >
                    <SelectTrigger><SelectValue placeholder="Selecciona una orden de compra" /></SelectTrigger>
                    <SelectContent>
                      {(purchaseOrders as PurchaseOrderDetailed[]).map((oc: PurchaseOrderDetailed) => (
                        <SelectItem key={oc.id_orden} value={String(oc.id_orden)}>
                          {oc.numero_orden}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
                <p className="text-xs text-muted-foreground">{editingEntry ? 'No se puede cambiar la orden en edición' : 'Se cargarán automáticamente el proveedor e insumos'}</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="id_proveedor">Proveedor</Label>
                <div className="px-3 py-2 rounded-md border border-input bg-muted text-sm min-h-10 flex items-center">
                  {formData.id_proveedor ? (
                    suppliers.find(s => (s.id_proveedor || s.id) === formData.id_proveedor)?.nombre_proveedor ||
                    suppliers.find(s => (s.id_proveedor || s.id) === formData.id_proveedor)?.nombre ||
                    'N/A'
                  ) : (
                    <span className="text-muted-foreground">Selecciona una orden de compra primero</span>
                  )}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                    <Label htmlFor="tipo_documento">Tipo Documento</Label>
                    <Select onValueChange={(value: "FACTURA" | "BOLETA" | "GUIA_REMISION") => setFormData(p => ({ ...p, tipo_documento: value }))} value={formData.tipo_documento}>
                        <SelectTrigger><SelectValue placeholder="Tipo de doc." /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="FACTURA">Factura</SelectItem>
                            <SelectItem value="BOLETA">Boleta</SelectItem>
                            <SelectItem value="GUIA_REMISION">Guía de Remisión</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="space-y-2">
                    <Label htmlFor="numero_documento">Nº Documento</Label>
                    <Input id="numero_documento" value={formData.numero_documento || ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(p => ({ ...p, numero_documento: e.target.value }))} required />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="fecha_documento">Fecha Documento</Label>
                    <Input id="fecha_documento" type="date" value={formData.fecha_documento || ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(p => ({ ...p, fecha_documento: e.target.value }))} required />
                </div>
            </div>
            <div className="space-y-2">
                <Label htmlFor="observaciones">Observaciones</Label>
                <Textarea id="observaciones" value={formData.observaciones || ''} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData(p => ({ ...p, observaciones: e.target.value }))} />
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Detalles del Ingreso</h3>
                <Button type="button" variant="outline" size="sm" onClick={addDetail}><Plus className="mr-2 h-4 w-4" /> Añadir Insumo</Button>
              </div>
              
              {formData.detalles && formData.detalles.length === 0 && (
                <div className="p-4 rounded-md bg-muted text-muted-foreground text-center">
                  Selecciona una orden de compra para cargar automáticamente los insumos
                </div>
              )}
              
              <div className="space-y-3">
                {(formData.detalles || []).map((detail, index) => (
                  <div key={index} className="p-3 rounded-md border bg-card space-y-3">
                    {/* Fila 1: Insumo */}
                    <div>
                      <label className="text-sm font-medium block mb-1">Insumo</label>
                      <Select 
                        onValueChange={(value: string) => handleDetailChange(index, 'id_insumo', value)} 
                        value={String(detail.id_insumo || '')}
                      >
                        <SelectTrigger><SelectValue placeholder="Selecciona insumo" /></SelectTrigger>
                        <SelectContent>
                          {insumos.map((i: Insumo) => (
                            <SelectItem key={i.id_insumo || i.id} value={String(i.id_insumo || i.id)}>
                              {i.nombre_insumo || i.nombre || i.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    {/* Fila 2: Cantidades y Precio */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <label className="text-sm font-medium block mb-1">Cant. Ordenada</label>
                        <Input 
                          type="number" 
                          placeholder="0" 
                          value={detail.cantidad_ordenada} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'cantidad_ordenada', e.target.value)}
                          readOnly
                          className="bg-muted"
                        />
                        <p className="text-xs text-muted-foreground mt-1">De la orden de compra</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium block mb-1">Cant. Ingresada *</label>
                        <Input 
                          type="number" 
                          placeholder="0" 
                          value={detail.cantidad_ingresada} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'cantidad_ingresada', e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground mt-1">Lo que realmente llegó</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium block mb-1">Precio Unit. (S/)</label>
                        <Input 
                          type="number" 
                          placeholder="0.00" 
                          value={detail.precio_unitario} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleDetailChange(index, 'precio_unitario', e.target.value)}
                          readOnly
                          className="bg-muted"
                        />
                        <p className="text-xs text-muted-foreground mt-1">De la orden de compra</p>
                      </div>
                    </div>
                    
                    {/* Fila 3: Subtotal y Botón Eliminar */}
                    <div className="flex items-end gap-3">
                      <div className="flex-1">
                        <label className="text-sm font-medium block mb-1">Subtotal (S/)</label>
                        <Input 
                          readOnly 
                          value={(detail.subtotal || 0).toFixed(2)} 
                          className="bg-muted font-semibold" 
                        />
                      </div>
                      <Button 
                        type="button" 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => removeDetail(index)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    {/* Indicador de diferencia */}
                    {detail.cantidad_ingresada !== detail.cantidad_ordenada && (
                      <div className={`text-xs p-2 rounded ${
                        detail.cantidad_ingresada < detail.cantidad_ordenada 
                          ? 'bg-yellow-50 text-yellow-700' 
                          : 'bg-green-50 text-green-700'
                      }`}>
                        {detail.cantidad_ingresada < detail.cantidad_ordenada 
                          ? `⚠️ Faltan ${detail.cantidad_ordenada - detail.cantidad_ingresada} unidades`
                          : `✓ ${detail.cantidad_ingresada - detail.cantidad_ordenada} unidades extra`
                        }
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            
            <Separator />

            <div className="flex justify-between items-center">
                <div className="text-lg font-bold">Monto Total: S/ {(formData.monto_total || 0).toFixed(2)}</div>
                <div className="flex gap-2">
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
                    <Button type="submit">{editingEntry ? 'Actualizar Ingreso' : 'Crear Ingreso'}</Button>
                </div>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
