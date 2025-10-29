import React, { useState, useEffect } from 'react';
import { Plus, Search, MoreVertical, Edit, Trash2, FileText, Calendar, User, Truck, ShoppingCart, Hash, DollarSign, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { API_BASE_URL } from '@/constants';

// --- CONFIGURACIÓN DE URL UNIFICADA ---
const SUPPLY_ENTRY_API_URL = `${API_BASE_URL}/v1/ingresos-productos`;

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

// --- DATOS MOCK (simulando datos del backend) ---
const mockSuppliers = [
  { id: 1, name: "Proveedor de Harinas S.A." },
  { id: 2, name: "Lácteos del Sur" },
  { id: 3, name: "Distribuidora de Frutas y Verduras" },
];

const mockPurchaseOrders = [
  { id: 1, number: "OC-2023-001", supplierId: 1 },
  { id: 2, number: "OC-2023-002", supplierId: 2 },
  { id: 3, number: "OC-2023-003", supplierId: 1 },
];

const mockInsumos = [
    { id: 1, name: "Harina de trigo", unit: "kg" },
    { id: 2, name: "Azúcar refinada", unit: "kg" },
    { id: 3, name: "Huevos frescos", unit: "unidades" },
    { id: 4, name: "Mantequilla", unit: "kg" },
];

export function SupplyEntryManager() {
  const [entries, setEntries] = useState<SupplyEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<SupplyEntry | null>(null);
  
  const [formData, setFormData] = useState<Partial<SupplyEntry>>({
    detalles: [],
    estado: "PENDIENTE",
    tipo_documento: "FACTURA",
  });

  const mapApiToUi = (apiEntry: any): SupplyEntry => {
    const supplier = mockSuppliers.find(s => s.id === apiEntry.id_proveedor);
    return {
      ...apiEntry,
      id_ingreso: apiEntry.id_ingreso,
      nombre_proveedor: supplier?.name || 'N/A',
      fecha_ingreso: new Date(apiEntry.fecha_ingreso).toISOString().split('T')[0],
      fecha_documento: new Date(apiEntry.fecha_documento).toISOString().split('T')[0],
      detalles: (apiEntry.detalles || []).map((detail: any) => {
        const insumo = mockInsumos.find(i => i.id === detail.id_insumo);
        return {
          ...detail,
          nombre_insumo: insumo?.name || 'Insumo desconocido',
          fecha_vencimiento: detail.fecha_vencimiento ? new Date(detail.fecha_vencimiento).toISOString().split('T')[0] : undefined,
        };
      }),
    };
  };

  const fetchEntries = async () => {
    try {
      const response = await fetch(SUPPLY_ENTRY_API_URL);
      if (!response.ok) throw new Error('Error al cargar los ingresos');
      const result = await response.json();
      const mappedEntries = (result.data || result).map(mapApiToUi);
      setEntries(mappedEntries);
    } catch (error) {
      console.error("Error fetching supply entries:", error);
      // En un caso real, aquí podrías poner datos mock para desarrollo
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const handleDetailChange = (index: number, field: keyof SupplyEntryDetail, value: any) => {
    const newDetails = [...(formData.detalles || [])];
    const detail = newDetails[index];
    
    let updatedDetail = { ...detail, [field]: value };

    if (field === 'id_insumo') {
        const insumo = mockInsumos.find(i => i.id === Number(value));
        updatedDetail.nombre_insumo = insumo?.name;
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
      await fetchEntries();
      setIsDialogOpen(false);
    } catch (error) {
      console.error("Submit error:", error);
      alert(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const handleEdit = (entry: SupplyEntry) => {
    setEditingEntry(entry);
    setFormData(mapApiToUi(entry));
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea anular este ingreso?")) return;
    try {
      // Lógica de anulación (puede ser un PUT o un DELETE)
      const response = await fetch(`${SUPPLY_ENTRY_API_URL}/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Error al anular el ingreso');
      await fetchEntries();
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
              onChange={(e) => setSearchTerm(e.target.value)}
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
                <Input id="numero_ingreso" value={formData.numero_ingreso || ''} onChange={e => setFormData(p => ({ ...p, numero_ingreso: e.target.value }))} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="id_orden_compra">Orden de Compra</Label>
                <Select onValueChange={value => setFormData(p => ({ ...p, id_orden_compra: Number(value) }))} value={String(formData.id_orden_compra || '')}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar OC" /></SelectTrigger>
                  <SelectContent>
                    {mockPurchaseOrders.map(oc => <SelectItem key={oc.id} value={String(oc.id)}>{oc.number}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="id_proveedor">Proveedor</Label>
                <Select onValueChange={value => setFormData(p => ({ ...p, id_proveedor: Number(value) }))} value={String(formData.id_proveedor || '')} required>
                  <SelectTrigger><SelectValue placeholder="Seleccionar Proveedor" /></SelectTrigger>
                  <SelectContent>
                    {mockSuppliers.map(s => <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>)}
                  </SelectContent>
                </Select>
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
                    <Input id="numero_documento" value={formData.numero_documento || ''} onChange={e => setFormData(p => ({ ...p, numero_documento: e.target.value }))} required />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="fecha_documento">Fecha Documento</Label>
                    <Input id="fecha_documento" type="date" value={formData.fecha_documento || ''} onChange={e => setFormData(p => ({ ...p, fecha_documento: e.target.value }))} required />
                </div>
            </div>
            <div className="space-y-2">
                <Label htmlFor="observaciones">Observaciones</Label>
                <Textarea id="observaciones" value={formData.observaciones || ''} onChange={e => setFormData(p => ({ ...p, observaciones: e.target.value }))} />
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Detalles del Ingreso</h3>
                <Button type="button" variant="outline" size="sm" onClick={addDetail}><Plus className="mr-2 h-4 w-4" /> Añadir Insumo</Button>
              </div>
              <div className="space-y-2">
                {(formData.detalles || []).map((detail, index) => (
                  <div key={index} className="grid grid-cols-12 gap-2 items-center p-2 rounded-md border">
                    <div className="col-span-3">
                      <Select onValueChange={value => handleDetailChange(index, 'id_insumo', value)} value={String(detail.id_insumo || '')}>
                        <SelectTrigger><SelectValue placeholder="Insumo" /></SelectTrigger>
                        <SelectContent>
                          {mockInsumos.map(i => <SelectItem key={i.id} value={String(i.id)}>{i.name}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-2"><Input type="number" placeholder="Cant. Ordenada" value={detail.cantidad_ordenada} onChange={e => handleDetailChange(index, 'cantidad_ordenada', e.target.value)} /></div>
                    <div className="col-span-2"><Input type="number" placeholder="Cant. Ingresada" value={detail.cantidad_ingresada} onChange={e => handleDetailChange(index, 'cantidad_ingresada', e.target.value)} /></div>
                    <div className="col-span-2"><Input type="number" placeholder="Precio Unit." value={detail.precio_unitario} onChange={e => handleDetailChange(index, 'precio_unitario', e.target.value)} /></div>
                    <div className="col-span-2"><Input readOnly value={(detail.subtotal || 0).toFixed(2)} className="bg-muted" /></div>
                    <div className="col-span-1"><Button type="button" variant="ghost" size="icon" onClick={() => removeDetail(index)}><Trash2 className="h-4 w-4 text-red-500" /></Button></div>
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
