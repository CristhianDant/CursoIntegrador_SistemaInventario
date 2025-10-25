import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, Package, AlertTriangle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
impo  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gestión de Insumos</h1>
      <p className="text-muted-foreground mb-6">Gestiona los insumos y materias primas del sistema</p>

      <div className="grid gap-4">
        {supplies.map((supply) => (
          <div key={supply.id_insumo} className="p-4 border rounded-lg">
            <h3 className="font-semibold">{supply.nombre}</h3>
            <p className="text-sm text-muted-foreground">{supply.descripcion}</p>
            <p>Código: {supply.codigo}</p>
            <p>Stock: {supply.stock_actual}</p>
          </div>
        ))}
      </div>
    </div>
  );bleBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";

interface SupplyMovement {
  id: number;
  type: 'entrada' | 'salida' | 'ajuste';
  quantity: number;
  date: string;
  notes?: string;
  supplier?: string;
}

interface Supply {
  id_insumo: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  unidad_medida: string;
  stock_minimo: number;
  perecible: boolean;
  categoria: string;
  stock_actual: number;
  precio_promedio: number;
  fecha_registro: string;
  anulado: boolean;
}

// Mock data de proveedores
const suppliers = [
  "Proveedor ABC S.A.",
  "Distribuidora XYZ",
  "Alimentos Premium Ltda.",
  "Importadora Global",
  "Proveedor Local"
];

const mockSupplies: Supply[] = [
  {
    id_insumo: 1,
    codigo: "INS001",
    nombre: "Harina de Trigo Premium",
    descripcion: "Harina de trigo refinada para repostería",
    unidad_medida: "kg",
    stock_minimo: 10,
    perecible: false,
    categoria: "Harinas",
    stock_actual: 25,
    precio_promedio: 2.50,
    fecha_registro: "2024-09-01T10:00:00",
    anulado: false
  },
  {
    id_insumo: 2,
    codigo: "INS002",
    nombre: "Azúcar Refinada",
    descripcion: "Azúcar refinada blanca granulada",
    unidad_medida: "kg",
    stock_minimo: 15,
    perecible: false,
    categoria: "Endulzantes",
    stock_actual: 8,
    precio_promedio: 3.20,
    fecha_registro: "2024-08-20T14:30:00",
    anulado: false
  },
  {
    id_insumo: 3,
    codigo: "INS003",
    nombre: "Huevos Frescos",
    descripcion: "Huevos frescos de granja",
    unidad_medida: "unidad",
    stock_minimo: 50,
    perecible: true,
    categoria: "Proteínas",
    stock_actual: 120,
    precio_promedio: 0.25,
    fecha_registro: "2024-09-05T09:15:00",
    anulado: false
  },
  {
    id_insumo: 4,
    codigo: "INS004",
    nombre: "Mantequilla sin Sal",
    descripcion: "Mantequilla sin sal para repostería",
    unidad_medida: "kg",
    stock_minimo: 8,
    perecible: true,
    categoria: "Lácteos",
    stock_actual: 15,
    precio_promedio: 8.50,
    fecha_registro: "2024-08-15T16:45:00",
    anulado: false
  },
  {
    id_insumo: 5,
    codigo: "INS005",
    nombre: "Chocolate en Polvo",
    descripcion: "Chocolate en polvo puro para repostería",
    unidad_medida: "kg",
    stock_minimo: 10,
    perecible: false,
    categoria: "Cacaos",
    stock_actual: 5,
    precio_promedio: 12.00,
    fecha_registro: "2024-07-15T11:20:00",
    anulado: false
  }
];

export function InsumosManager() {
  const [supplies, setSupplies] = useState<Supply[]>(mockSupplies);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false);
  const [editingSupply, setEditingSupply] = useState<Supply | null>(null);
  const [selectedSupply, setSelectedSupply] = useState<Supply | null>(null);
  const [formData, setFormData] = useState<Partial<Supply>>({});
  const [movementData, setMovementData] = useState<Partial<SupplyMovement>>({});

  const categories = ["Harinas", "Endulzantes", "Proteínas", "Lácteos", "Cacaos", "Frutas", "Especias", "Conservantes"];

  // Cargar insumos desde API
  useEffect(() => {
    const fetchSupplies = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/insumos/?skip=0&limit=100');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            setSupplies(data.data);
          }
        } else {
          console.error('Error al cargar insumos:', await response.text());
        }
      } catch (error) {
        console.error('Error de conexión al cargar insumos:', error);
      }
    };

    fetchSupplies();
  }, []);

  const filteredSupplies = supplies.filter(supply => {
    const matchesSearch = supply.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         supply.categoria.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || supply.categoria === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Disponible': return 'bg-green-100 text-green-800';
      case 'Agotado': return 'bg-red-100 text-red-800';
      case 'Por Vencer': return 'bg-yellow-100 text-yellow-800';
      case 'Vencido': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editingSupply) {
      // TODO: Implementar actualización de insumo existente
      console.log('Actualización de insumo no implementada aún');
    } else {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/insumos/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            codigo: formData.codigo,
            nombre: formData.nombre,
            descripcion: formData.descripcion,
            unidad_medida: formData.unidad_medida,
            stock_minimo: formData.stock_minimo,
            perecible: formData.perecible || false,
            categoria: formData.categoria
          })
        });

        if (response.ok) {
          const data = await response.json();
          // Recargar insumos después de crear uno nuevo
          const suppliesResponse = await fetch('http://127.0.0.1:8000/api/v1/insumos/?skip=1&limit=100');
          if (suppliesResponse.ok) {
            const suppliesData = await suppliesResponse.json();
            if (suppliesData.success && suppliesData.data) {
              setSupplies(suppliesData.data);
            }
          }
          setIsDialogOpen(false);
          setEditingSupply(null);
          setFormData({});
        } else {
          console.error('Error al crear insumo:', await response.text());
        }
      } catch (error) {
        console.error('Error de conexión al crear insumo:', error);
      }
    }
  };

  const handleMovementSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedSupply || !movementData.type || !movementData.quantity) return;

    const newMovement: SupplyMovement = {
      id: Date.now(),
      type: movementData.type,
      quantity: movementData.quantity,
      date: movementData.date || new Date().toISOString().split('T')[0],
      notes: movementData.notes,
      supplier: movementData.type === 'entrada' ? movementData.supplier : undefined
    };

    setSupplies(prev =>
      prev.map(supply => {
        if (supply.id_insumo === selectedSupply.id_insumo) {
          const quantity = movementData.quantity || 0;
          const updatedStock = movementData.type === 'entrada'
            ? supply.stock_actual + quantity
            : supply.stock_actual - quantity;

          let newStatus = 'Disponible';
          if (updatedStock <= 0) newStatus = 'Agotado';
          else if (updatedStock <= supply.stock_minimo) newStatus = 'Por Vencer';

          return {
            ...supply,
            stock_actual: Math.max(0, updatedStock),
            status: newStatus
          };
        }
        return supply;
      })
    );

    setIsMovementDialogOpen(false);
    setSelectedSupply(null);
    setMovementData({});
  };

  const openEntryDialog = (supply: Supply) => {
    setSelectedSupply(supply);
    setMovementData({ type: 'entrada', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
  };

  const openExitDialog = (supply: Supply) => {
    setSelectedSupply(supply);
    setMovementData({ type: 'salida', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
  };

  const handleEdit = (supply: Supply) => {
    setEditingSupply(supply);
    setFormData(supply);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    setSupplies(prev => prev.filter(supply => supply.id_insumo !== id));
  };

  const openAddDialog = () => {
    setEditingSupply(null);
    setFormData({
      codigo: '',
      nombre: '',
      descripcion: '',
      unidad_medida: '',
      stock_minimo: 0,
      perecible: false,
      categoria: ''
    });
    setIsDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Insumos</h2>
          <p className="text-muted-foreground">Gestiona los insumos y materias primas del sistema</p>
        </div>

        <Button onClick={openAddDialog}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Insumo
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar insumos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Categoría" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las categorías</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="Disponible">Disponible</SelectItem>
                <SelectItem value="Agotado">Agotado</SelectItem>
                <SelectItem value="Por Vencer">Por Vencer</SelectItem>
                <SelectItem value="Vencido">Vencido</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de insumos */}
      <Card>
        <CardHeader>
          <CardTitle>Inventario de Insumos</CardTitle>
          <CardDescription>
            {filteredSupplies.length} insumos encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Stock Actual</TableHead>
                  <TableHead>Stock Mínimo</TableHead>
                  <TableHead>Unidad</TableHead>
                  <TableHead>Perecible</TableHead>
                  <TableHead>Precio Promedio</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSupplies.map((supply) => (
                  <TableRow key={supply.id_insumo}>
                    <TableCell>
                      <Badge variant="outline">{supply.codigo}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{supply.nombre}</div>
                      <div className="text-sm text-muted-foreground">{supply.descripcion}</div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{supply.categoria}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{supply.stock_actual}</div>
                    </TableCell>
                    <TableCell>{supply.stock_minimo}</TableCell>
                    <TableCell>{supply.unidad_medida}</TableCell>
                    <TableCell>
                      <Badge variant={supply.perecible ? "destructive" : "secondary"}>
                        {supply.perecible ? "Sí" : "No"}
                      </Badge>
                    </TableCell>
                    <TableCell>${supply.precio_promedio.toFixed(2)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(supply)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                          onClick={() => handleDelete(supply.id_insumo)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Dialog para nuevo/editar insumo */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingSupply ? "Editar Insumo" : "Nuevo Insumo"}
            </DialogTitle>
            <DialogDescription>
              {editingSupply ? "Modifica la información del insumo" : "Registra un nuevo insumo en el inventario"}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="codigo">Código</Label>
                <Input
                  id="codigo"
                  placeholder="Ej: INS001"
                  value={formData.codigo || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, codigo: e.target.value }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="nombre">Nombre del Insumo</Label>
                <Input
                  id="nombre"
                  placeholder="Ej: Harina de Trigo Premium"
                  value={formData.nombre || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, nombre: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="descripcion">Descripción</Label>
              <Textarea
                id="descripcion"
                placeholder="Descripción del insumo..."
                value={formData.descripcion || ""}
                onChange={(e) => setFormData(prev => ({ ...prev, descripcion: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="categoria">Categoría</Label>
                <Select value={formData.categoria || ""} onValueChange={(value: string) => setFormData(prev => ({ ...prev, categoria: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona una categoría" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(category => (
                      <SelectItem key={category} value={category}>{category}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="unidad_medida">Unidad de Medida</Label>
                <Select value={formData.unidad_medida || ""} onValueChange={(value: string) => setFormData(prev => ({ ...prev, unidad_medida: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona unidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="KG">Kilogramos (KG)</SelectItem>
                    <SelectItem value="L">Litros (L)</SelectItem>
                    <SelectItem value="G">Gramos (G)</SelectItem>
                    <SelectItem value="ML">Mililitros (ML)</SelectItem>
                    <SelectItem value="UNIDAD">Unidad</SelectItem>
                    <SelectItem value="CAJA">Caja</SelectItem>
                    <SelectItem value="PAQUETE">Paquete</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="stock_minimo">Stock Mínimo</Label>
                <Input
                  id="stock_minimo"
                  type="number"
                  step="0.01"
                  value={formData.stock_minimo || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, stock_minimo: parseFloat(e.target.value) }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="perecible">¿Es Perecible?</Label>
                <Select value={formData.perecible?.toString() || "false"} onValueChange={(value: string) => setFormData(prev => ({ ...prev, perecible: value === "true" }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona si es perecible" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="false">No perecible</SelectItem>
                    <SelectItem value="true">Perecible</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingSupply ? "Actualizar" : "Crear Insumo"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Dialog para movimientos */}
      <Dialog open={isMovementDialogOpen} onOpenChange={setIsMovementDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {movementData.type === 'entrada' ? 'Registrar Entrada' : 'Registrar Salida'}
            </DialogTitle>
            <DialogDescription>
              {selectedSupply?.nombre} - Stock actual: {selectedSupply?.stock_actual} {selectedSupply?.unidad_medida}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleMovementSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantity">Cantidad</Label>
                <Input
                  id="quantity"
                  type="number"
                  step="0.01"
                  placeholder={`Cantidad en ${selectedSupply?.unidad_medida}`}
                  value={movementData.quantity || ""}
                  onChange={(e) => setMovementData(prev => ({ ...prev, quantity: parseFloat(e.target.value) }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="date">Fecha</Label>
                <Input
                  id="date"
                  type="date"
                  value={movementData.date || ""}
                  onChange={(e) => setMovementData(prev => ({ ...prev, date: e.target.value }))}
                  required
                />
              </div>
            </div>

            {movementData.type === 'entrada' && (
              <div className="space-y-2">
                <Label htmlFor="supplier">Proveedor</Label>
                <Select value={movementData.supplier || ""} onValueChange={(value: string) => setMovementData(prev => ({ ...prev, supplier: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona proveedor" />
                  </SelectTrigger>
                  <SelectContent>
                    {suppliers.map(supplier => (
                      <SelectItem key={supplier} value={supplier}>{supplier}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="notes">Notas</Label>
              <Textarea
                id="notes"
                placeholder="Notas sobre el movimiento..."
                value={movementData.notes || ""}
                onChange={(e) => setMovementData(prev => ({ ...prev, notes: e.target.value }))}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setIsMovementDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                Registrar {movementData.type === 'entrada' ? 'Entrada' : 'Salida'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}