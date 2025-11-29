import { useState, useEffect, useMemo } from "react";
import { Plus, Search, Edit, Trash2, ChefHat, Eye, Package, DollarSign, Clock, FileText, X } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { SearchableSelect } from "./ui/searchable-select";
import { toast } from "sonner";
import { API_BASE_URL } from "../constants"; 
import { useAuth } from "../context/AuthContext"; 

const RECETAS_API_URL = `${API_BASE_URL}/v1/recetas`; 

// *** INTERFACES ***
interface RecipeIngredient {
  id: number;
  id_insumo: number;
  cantidad: number;
  costo_unitario: number;
  costo_total: number;
  es_opcional: boolean;
  observaciones: string;
  // UI fields
  nombre_insumo?: string;
  unidad_medida?: string;
}

interface Recipe {
  id: number;
  id_receta: number;
  id_producto: number;
  codigo_receta: string;
  nombre_receta: string; 
  descripcion: string;
  rendimiento_producto_terminado: number; 
  costo_estimado: number;
  version: number; 
  estado: "ACTIVA" | "INACTIVA";
  fecha_creacion?: string;
  detalles: RecipeIngredient[];
  // UI fields
  nombre_producto?: string;
}

interface Insumo {
  id_insumo?: number;
  id?: number;
  nombre_insumo?: string;
  nombre?: string;
  unidad_medida?: string;
  precio_unitario?: number;
  costo?: number;
}

interface Producto {
  id_producto?: number;
  id?: number;
  nombre?: string;
  nombre_producto?: string;
}

export function RecipeManager() {
  const { canWrite } = useAuth();
  const canEditRecipes = canWrite('RECETAS');
  
  const [recipes, setRecipes] = useState<Recipe[]>([]);  
  const [insumos, setInsumos] = useState<Insumo[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [ultimosPrecios, setUltimosPrecios] = useState<Record<number, number>>({});
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [formData, setFormData] = useState<Partial<Recipe>>({
    detalles: [], 
    id_producto: 0,
    rendimiento_producto_terminado: 1,
    version: 1,
    estado: "ACTIVA",
  });

  // Opciones para SearchableSelect de insumos
  const insumoOptions = useMemo(() => {
    return insumos.map(insumo => ({
      value: String(insumo.id_insumo || insumo.id),
      label: `${insumo.nombre_insumo || insumo.nombre} (${insumo.unidad_medida || 'unidad'})`,
    }));
  }, [insumos]);

  // --- Funciones de carga de datos ---
  const loadAllData = async () => {
    try {
      const [recetasRes, insumosRes, productosRes, preciosRes] = await Promise.all([
        fetch(RECETAS_API_URL),
        fetch(`${API_BASE_URL}/v1/insumos`),
        fetch(`${API_BASE_URL}/v1/productos_terminados`),
        fetch(`${API_BASE_URL}/v1/insumos/precios/ultimos`),
      ]);

      // Cargar últimos precios de insumos
      let preciosMap: Record<number, number> = {};
      if (preciosRes.ok) {
        const preciosData = await preciosRes.json();
        preciosMap = preciosData.data || preciosData || {};
        setUltimosPrecios(preciosMap);
      }

      // Cargar insumos
      let insumosList: Insumo[] = [];
      if (insumosRes.ok) {
        const insumosData = await insumosRes.json();
        insumosList = Array.isArray(insumosData) ? insumosData : (insumosData.data || []);
        setInsumos(insumosList);
      }

      // Cargar productos
      let productosList: Producto[] = [];
      if (productosRes.ok) {
        const productosData = await productosRes.json();
        productosList = Array.isArray(productosData) ? productosData : (productosData.data || []);
        setProductos(productosList);
      }

      // Cargar recetas y mapear con insumos/productos
      if (recetasRes.ok) {
        const recetasData = await recetasRes.json();
        const recetasList = Array.isArray(recetasData) ? recetasData : (recetasData.data || []);
        
        const mappedRecipes = recetasList.map((recipe: any) => {
          const producto = productosList.find(p => (p.id_producto || p.id) === recipe.id_producto);
          
          return {
            ...recipe,
            id: recipe.id_receta,
            nombre_producto: producto?.nombre_producto || producto?.nombre || 'Producto no asignado',
            detalles: (recipe.detalles || []).map((detail: any) => {
              const insumo = insumosList.find(i => (i.id_insumo || i.id) === detail.id_insumo);
              return {
                ...detail,
                id: detail.id_receta_detalle || detail.id || Date.now() + Math.random(),
                nombre_insumo: insumo?.nombre_insumo || insumo?.nombre || 'Insumo desconocido',
                unidad_medida: insumo?.unidad_medida || 'unidad',
              };
            }),
          };
        });
        
        setRecipes(mappedRecipes);
      }
    } catch (error) {
      console.error("Error loading data:", error);
      toast.error("Error al cargar los datos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const calculateTotalCost = (details = formData.detalles || []) => {
    return details.reduce((total, ing) => total + (ing.costo_total || 0), 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const recetaId = editingRecipe?.id_receta || 0;
    const isEditing = recetaId !== 0;
    
    const url = isEditing ? `${RECETAS_API_URL}/${recetaId}` : RECETAS_API_URL;
    const method = isEditing ? 'PUT' : 'POST';

    const totalCost = calculateTotalCost(formData.detalles);
    
    const bodyData = {
      id_producto: formData.id_producto || 0,
      codigo_receta: formData.codigo_receta || '',
      nombre_receta: formData.nombre_receta || '',
      descripcion: formData.descripcion || '',
      rendimiento_producto_terminado: formData.rendimiento_producto_terminado || 1,
      costo_estimado: totalCost,
      version: formData.version || 1,
      estado: formData.estado || 'ACTIVA',
      detalles: (formData.detalles || []).map(detail => ({
        id_insumo: detail.id_insumo,
        cantidad: detail.cantidad,
        costo_unitario: detail.costo_unitario,
        costo_total: detail.costo_total,
        es_opcional: detail.es_opcional || false,
        observaciones: detail.observaciones || '',
      })),
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.data || responseData.message || responseData.detail || 'Error al guardar la receta');
      }
      
      toast.success(isEditing ? 'Receta actualizada correctamente' : 'Receta creada correctamente');
      await loadAllData();
      setIsDialogOpen(false);
      setEditingRecipe(null);
      resetForm();
    } catch (error) {
      console.error('=== ERROR ===', error);
      toast.error(error instanceof Error ? error.message : 'Error desconocido');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro que desea eliminar esta receta?")) return;
    
    try {
      const response = await fetch(`${RECETAS_API_URL}/${id}`, { method: 'DELETE' });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.data || error.message || 'Error al eliminar');
      }

      toast.success('Receta eliminada correctamente');
      setRecipes(prev => prev.filter(r => r.id !== id));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al eliminar');
    }
  };

  const resetForm = () => {
    setFormData({
      detalles: [],
      id_producto: 0,
      nombre_receta: '',
      descripcion: '',
      codigo_receta: '',
      rendimiento_producto_terminado: 1,
      costo_estimado: 0,
      version: 1,
      estado: 'ACTIVA',
    });
  };

  const openAddDialog = () => {
    setEditingRecipe(null);
    resetForm();
    setIsDialogOpen(true);
  };

  const handleEdit = (recipe: Recipe) => {
    setEditingRecipe(recipe);
    setFormData({
      ...recipe,
      detalles: recipe.detalles.map(d => ({
        ...d,
        id: d.id || Date.now() + Math.random(),
      })),
    });
    setIsDialogOpen(true);
  };

  const handleViewDetails = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setIsDetailDialogOpen(true);
  };

  const addIngredient = () => {
    const newIngredient: RecipeIngredient = {
      id: Date.now() + Math.random(),
      id_insumo: 0,
      cantidad: 0,
      costo_unitario: 0,
      costo_total: 0,
      es_opcional: false,
      observaciones: '',
      nombre_insumo: '',
      unidad_medida: '',
    };
    setFormData(prev => ({
      ...prev,
      detalles: [...(prev.detalles || []), newIngredient],
    }));
  };

  const updateIngredient = (index: number, field: keyof RecipeIngredient, value: any) => {
    const details = [...(formData.detalles || [])];
    const detail = details[index];
    
    if (field === 'id_insumo') {
      const insumoId = Number(value);
      const selectedInsumo = insumos.find(i => (i.id_insumo || i.id) === insumoId);
      if (selectedInsumo) {
        // Usar el último precio de compra del backend, si existe
        const costoSugerido = ultimosPrecios[insumoId] || 0;
        details[index] = {
          ...detail,
          id_insumo: insumoId,
          nombre_insumo: selectedInsumo.nombre_insumo || selectedInsumo.nombre,
          unidad_medida: selectedInsumo.unidad_medida || 'unidad',
          costo_unitario: costoSugerido,
          costo_total: (detail.cantidad || 0) * costoSugerido,
        };
      }
    } else if (field === 'cantidad') {
      const newQuantity = parseFloat(value) || 0;
      details[index] = {
        ...detail,
        cantidad: newQuantity,
        costo_total: newQuantity * (detail.costo_unitario || 0),
      };
    } else if (field === 'costo_unitario') {
      const newCost = parseFloat(value) || 0;
      details[index] = {
        ...detail,
        costo_unitario: newCost,
        costo_total: (detail.cantidad || 0) * newCost,
      };
    } else {
      details[index] = { ...detail, [field]: value };
    }
    
    setFormData(prev => ({ ...prev, detalles: details }));
  };

  const removeIngredient = (index: number) => {
    const details = [...(formData.detalles || [])];
    details.splice(index, 1);
    setFormData(prev => ({ ...prev, detalles: details }));
  };

  const filteredRecipes = recipes.filter(recipe => {
    const name = recipe.nombre_receta || '';
    const description = recipe.descripcion || '';
    const code = recipe.codigo_receta || '';
    const searchLower = searchTerm.toLowerCase();
    
    return name.toLowerCase().includes(searchLower) ||
           description.toLowerCase().includes(searchLower) ||
           code.toLowerCase().includes(searchLower);
  });

  const getEstadoBadgeVariant = (estado: string) => {
    return estado === 'ACTIVA' ? 'default' : 'secondary';
  };

  // --- RENDERIZADO ---
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ChefHat className="h-7 w-7 text-primary" />
            Gestión de Recetas
          </h2>
          <p className="text-muted-foreground">Administra las recetas y calcula costos de producción</p>
        </div>
        
        {canEditRecipes && (
          <Button onClick={openAddDialog}>
            <Plus className="h-4 w-4 mr-2" />
            Nueva Receta
          </Button>
        )}
      </div>

      {/* Búsqueda */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar recetas por nombre, código o descripción..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Lista de recetas en Cards */}
      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Cargando recetas...</div>
      ) : filteredRecipes.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          No se encontraron recetas
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecipes.map((recipe) => (
            <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{recipe.nombre_receta}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {recipe.descripcion || 'Sin descripción'}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="ml-2 font-mono">
                    {recipe.codigo_receta}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Info del producto */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Package className="h-4 w-4" />
                  <span>{recipe.nombre_producto}</span>
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1">
                    <ChefHat className="h-4 w-4 text-muted-foreground" />
                    <span>v{recipe.version}</span>
                  </div>
                  <Badge variant="outline">
                    {recipe.detalles?.length || 0} ingredientes
                  </Badge>
                  <Badge variant={getEstadoBadgeVariant(recipe.estado)}>
                    {recipe.estado}
                  </Badge>
                </div>

                {/* Rendimiento y Costo */}
                <div className="space-y-2 pt-2 border-t">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Rendimiento:</span>
                    <span className="font-medium">{recipe.rendimiento_producto_terminado} unidades</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-semibold">Costo Estimado:</span>
                    <span className="font-bold text-green-600 text-lg">
                      S/ {(recipe.costo_estimado || 0).toFixed(2)}
                    </span>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewDetails(recipe)}
                    className="flex-1"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Ver Receta
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(recipe)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(recipe.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal Ver Detalles de Receta */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          {selectedRecipe && (
            <>
              <DialogHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <DialogTitle className="text-xl flex items-center gap-2">
                      <ChefHat className="h-5 w-5 text-primary" />
                      {selectedRecipe.nombre_receta}
                    </DialogTitle>
                    <DialogDescription className="mt-1">
                      {selectedRecipe.descripcion || 'Sin descripción'}
                    </DialogDescription>
                  </div>
                  <Badge variant={getEstadoBadgeVariant(selectedRecipe.estado)} className="ml-2">
                    {selectedRecipe.estado}
                  </Badge>
                </div>
              </DialogHeader>

              {/* Información General */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
                <div className="bg-muted/50 rounded-lg p-3 text-center">
                  <FileText className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Código</p>
                  <p className="font-mono font-semibold">{selectedRecipe.codigo_receta}</p>
                </div>
                <div className="bg-muted/50 rounded-lg p-3 text-center">
                  <Package className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Rendimiento</p>
                  <p className="font-semibold">{selectedRecipe.rendimiento_producto_terminado} unidades</p>
                </div>
                <div className="bg-muted/50 rounded-lg p-3 text-center">
                  <Clock className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Versión</p>
                  <p className="font-semibold">v{selectedRecipe.version}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3 text-center border border-green-200">
                  <DollarSign className="h-5 w-5 mx-auto mb-1 text-green-600" />
                  <p className="text-xs text-green-600">Costo Total</p>
                  <p className="font-bold text-green-700 text-lg">S/ {(selectedRecipe.costo_estimado || 0).toFixed(2)}</p>
                </div>
              </div>

              <Separator />

              {/* Producto Asociado */}
              <div className="py-2">
                <p className="text-sm text-muted-foreground mb-1">Producto Terminado:</p>
                <p className="font-medium flex items-center gap-2">
                  <Package className="h-4 w-4 text-primary" />
                  {selectedRecipe.nombre_producto}
                </p>
              </div>

              <Separator />

              {/* Lista de Ingredientes */}
              <div className="space-y-3">
                <h4 className="font-semibold flex items-center gap-2">
                  <ChefHat className="h-4 w-4" />
                  Ingredientes ({selectedRecipe.detalles?.length || 0})
                </h4>
                
                {selectedRecipe.detalles && selectedRecipe.detalles.length > 0 ? (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>#</TableHead>
                          <TableHead>Insumo</TableHead>
                          <TableHead className="text-right">Cantidad</TableHead>
                          <TableHead className="text-right">Costo Unit.</TableHead>
                          <TableHead className="text-right">Subtotal</TableHead>
                          <TableHead className="text-center">Opcional</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedRecipe.detalles.map((detail, index) => (
                          <TableRow key={detail.id}>
                            <TableCell className="text-muted-foreground">{index + 1}</TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">{detail.nombre_insumo}</p>
                                {detail.observaciones && (
                                  <p className="text-xs text-muted-foreground">{detail.observaciones}</p>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              {detail.cantidad} {detail.unidad_medida}
                            </TableCell>
                            <TableCell className="text-right">
                              S/ {(detail.costo_unitario || 0).toFixed(2)}
                            </TableCell>
                            <TableCell className="text-right font-medium">
                              S/ {(detail.costo_total || 0).toFixed(2)}
                            </TableCell>
                            <TableCell className="text-center">
                              {detail.es_opcional ? (
                                <Badge variant="outline">Sí</Badge>
                              ) : (
                                <span className="text-muted-foreground">-</span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                        {/* Fila de Total */}
                        <TableRow className="bg-muted/50 font-semibold">
                          <TableCell colSpan={4} className="text-right">
                            COSTO TOTAL:
                          </TableCell>
                          <TableCell className="text-right text-green-600 text-lg">
                            S/ {(selectedRecipe.costo_estimado || 0).toFixed(2)}
                          </TableCell>
                          <TableCell></TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground border rounded-md">
                    Esta receta no tiene ingredientes registrados
                  </div>
                )}
              </div>

              {/* Botones de acción */}
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setIsDetailDialogOpen(false)}>
                  Cerrar
                </Button>
                {canEditRecipes && (
                  <Button onClick={() => {
                    setIsDetailDialogOpen(false);
                    handleEdit(selectedRecipe);
                  }}>
                    <Edit className="h-4 w-4 mr-2" />
                    Editar Receta
                  </Button>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Modal Crear/Editar Receta */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingRecipe ? "Editar Receta" : "Nueva Receta"}
            </DialogTitle>
            <DialogDescription>
              {editingRecipe ? "Modifica la información de la receta" : "Crea una nueva receta con insumos y costos"}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Información básica */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nombre_receta">Nombre de la Receta *</Label>
                <Input
                  id="nombre_receta"
                  placeholder="Ej: Pastel de Chocolate"
                  value={formData.nombre_receta || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, nombre_receta: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="codigo_receta">Código de Receta *</Label>
                <Input
                  id="codigo_receta"
                  placeholder="Ej: REC-001"
                  value={formData.codigo_receta || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, codigo_receta: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="id_producto">Producto Terminado *</Label>
              <Select 
                value={formData.id_producto?.toString() || ""}
                onValueChange={(value: string) => setFormData(prev => ({ ...prev, id_producto: Number(value) }))}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar producto" />
                </SelectTrigger>
                <SelectContent>
                  {productos.map(producto => (
                    <SelectItem 
                      key={producto.id_producto || producto.id} 
                      value={String(producto.id_producto || producto.id)}
                    >
                      {producto.nombre_producto || producto.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="descripcion">Descripción</Label>
              <Textarea
                id="descripcion"
                placeholder="Descripción breve de la receta"
                value={formData.descripcion || ""}
                onChange={(e) => setFormData(prev => ({ ...prev, descripcion: e.target.value }))}
                rows={2}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rendimiento">Rendimiento (Unidades)</Label>
                <Input
                  id="rendimiento"
                  type="number"
                  min="1"
                  value={formData.rendimiento_producto_terminado || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, rendimiento_producto_terminado: parseInt(e.target.value) }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="version">Versión</Label>
                <Input
                  id="version"
                  type="number"
                  step="0.1"
                  min="1"
                  value={formData.version || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, version: parseFloat(e.target.value) }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estado">Estado</Label>
                <Select 
                  value={formData.estado || "ACTIVA"}
                  onValueChange={(value: "ACTIVA" | "INACTIVA") => setFormData(prev => ({ ...prev, estado: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ACTIVA">Activa</SelectItem>
                    <SelectItem value="INACTIVA">Inactiva</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            {/* Ingredientes */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Ingredientes (Insumos)</Label>
                <Button type="button" variant="outline" onClick={addIngredient}>
                  <Plus className="h-4 w-4 mr-2" />
                  Agregar Insumo
                </Button>
              </div>

              {(formData.detalles || []).length === 0 ? (
                <div className="text-center py-6 text-muted-foreground border-2 border-dashed rounded-md">
                  No hay ingredientes. Haz clic en "Agregar Insumo" para comenzar.
                </div>
              ) : (
                <div className="space-y-3">
                  {(formData.detalles || []).map((detail, index) => (
                    <div key={detail.id} className="grid grid-cols-12 gap-2 p-3 border rounded-md bg-muted/30 items-end">
                      <div className="col-span-3 space-y-1">
                        <Label className="text-xs">Insumo</Label>
                        <SearchableSelect
                          options={insumoOptions}
                          value={detail.id_insumo?.toString() || ""}
                          onValueChange={(value) => updateIngredient(index, 'id_insumo', value)}
                          placeholder="Buscar insumo..."
                        />
                      </div>

                      <div className="col-span-2 space-y-1">
                        <Label className="text-xs">Cantidad</Label>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                          value={detail.cantidad || ""}
                          onChange={(e) => updateIngredient(index, 'cantidad', e.target.value)}
                        />
                      </div>

                      <div className="col-span-1 space-y-1">
                        <Label className="text-xs">Unidad</Label>
                        <Input
                          value={detail.unidad_medida || "-"}
                          disabled
                          className="bg-muted text-center"
                        />
                      </div>

                      <div className="col-span-2 space-y-1">
                        <Label className="text-xs">Costo Unit.</Label>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                          value={detail.costo_unitario || ""}
                          onChange={(e) => updateIngredient(index, 'costo_unitario', e.target.value)}
                        />
                      </div>

                      <div className="col-span-2 space-y-1">
                        <Label className="text-xs">Subtotal</Label>
                        <Input
                          value={`S/ ${(detail.costo_total || 0).toFixed(2)}`}
                          disabled
                          className="bg-muted font-medium text-green-600"
                        />
                      </div>

                      <div className="col-span-2 flex justify-end">
                        <Button 
                          type="button" 
                          variant="ghost" 
                          size="sm"
                          onClick={() => removeIngredient(index)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <Separator />

            {/* Costo Total */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-green-700">Costo Estimado Total:</span>
                <span className="text-2xl font-bold text-green-700">
                  S/ {calculateTotalCost().toFixed(2)}
                </span>
              </div>
            </div>

            {/* Botones */}
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingRecipe ? "Actualizar Receta" : "Crear Receta"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}