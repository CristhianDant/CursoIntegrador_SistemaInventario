import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, ChefHat } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";

// NOTA: Asegúrate de que este archivo exista en tu proyecto.
import { API_BASE_URL } from "../constants"; 

// --- CONFIGURACIÓN DE URL UNIFICADA ---
const RECETAS_API_URL = `${API_BASE_URL}/v1/recetas`; 
// --------------------------------------

// *** INTERFACES AJUSTADAS AL MODELO DE LA API ***

interface RecipeIngredient {
  // Campos para la Interfaz (UI)
  id: number; // ID único para el frontend (key de React)
  unit: string; // Unidad para mostrar en el select
  costo_total: number; // Costo calculado para mostrar

  // Campos del Backend (detalles)
  id_insumo: number; // ID del Insumo (Select value)
  cantidad: number; // Cantidad (Input value)
  costo_unitario: number; // Costo unitario del insumo (calculado o de la lista estática)
  es_opcional: boolean;
  observaciones: string;
}

interface Recipe {
  id: number; // ID principal usado en el frontend, mapea a id_producto
  
  // Campos del Backend
  id_producto: number;
  codigo_receta: string;
  nombre_receta: string; 
  descripcion: string;
  rendimiento_producto_terminado: number; 
  costo_estimado: number;
  version: number; 
  estado: "ACTIVA" | "INACTIVA";
  detalles: RecipeIngredient[];
}
// ***************************************************************

// Lista de insumos (disponibles en tu sistema de inventario)
const availableIngredients = [
  { id: 1, name: "Harina de trigo", unit: "kg", currentStock: 25, costPerUnit: 1.2 },
  { id: 2, name: "Azúcar refinada", unit: "kg", currentStock: 15, costPerUnit: 2.5 },
  { id: 3, name: "Huevos frescos", unit: "unidades", currentStock: 200, costPerUnit: 0.33 },
  { id: 4, name: "Mantequilla", unit: "kg", currentStock: 8, costPerUnit: 8.5 },
  { id: 5, name: "Leche entera", unit: "litros", currentStock: 12, costPerUnit: 1.8 },
  { id: 6, name: "Chocolate negro 70%", unit: "kg", currentStock: 5, costPerUnit: 15.0 },
  { id: 7, name: "Vainilla líquida", unit: "ml", currentStock: 500, costPerUnit: 0.08 },
  { id: 8, name: "Polvo de hornear", unit: "g", currentStock: 2000, costPerUnit: 0.01 },
];


export function RecipeManager() {
  const [recipes, setRecipes] = useState<Recipe[]>([]); 
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  
  const [formData, setFormData] = useState<Partial<Recipe>>({
    detalles: [], 
    id_producto: 0,
    rendimiento_producto_terminado: 1,
    version: 1,
    estado: "ACTIVA",
  });

  // --- Funciones de Lógica y Mapeo ---

  // Mapea la respuesta del API a la estructura del Frontend (UI)
  const mapApiToUi = (apiRecipe: any): Recipe => {
    return {
        id: apiRecipe.id_producto, 
        id_producto: apiRecipe.id_producto || 0,
        nombre_receta: apiRecipe.nombre_receta || '',
        descripcion: apiRecipe.descripcion || '',
        codigo_receta: apiRecipe.codigo_receta || '',
        rendimiento_producto_terminado: apiRecipe.rendimiento_producto_terminado || 1,
        costo_estimado: apiRecipe.costo_estimado || 0,
        version: apiRecipe.version || 1,
        estado: apiRecipe.estado || 'ACTIVA',

        detalles: (apiRecipe.detalles || []).map((detail: any) => {
            const ingredientData = availableIngredients.find(i => i.id === detail.id_insumo);
            const costoUnitario = detail.costo_unitario || ingredientData?.costPerUnit || 0;

            return {
                id: detail.id || Date.now() + Math.random(), 
                id_insumo: detail.id_insumo,
                cantidad: detail.cantidad,
                costo_unitario: costoUnitario,
                costo_total: detail.costo_total || (detail.cantidad || 0) * costoUnitario,
                es_opcional: detail.es_opcional || false,
                observaciones: detail.observaciones || '',
                unit: ingredientData?.unit || 'unidades', // Campo de UI
            }
        }),
    };
  };

  const fetchRecipes = async () => {
    try {
        const response = await fetch(RECETAS_API_URL, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) {
            throw new Error('Error al cargar las recetas');
        }
        const rawData = await response.json();
        
        const mappedRecipes: Recipe[] = (rawData.data || rawData || []).map(mapApiToUi);
        
        setRecipes(mappedRecipes);
    } catch (error) {
        console.error("Error fetching recipes:", error);
    }
  };

  const calculateTotalCost = (details = formData.detalles || []) => {
    return details.reduce((total, ing) => total + ing.costo_total, 0);
  };

  const createOrUpdateReceta = async (recipeData: Partial<Recipe>) => {
      const recetaId = recipeData.id_producto || 0; 
      const isEditing = recetaId !== 0;
      
      const url = isEditing ? `${RECETAS_API_URL}/${recetaId}` : RECETAS_API_URL;
      const method = isEditing ? 'PUT' : 'POST';

      const totalCost = calculateTotalCost(recipeData.detalles);
      
      // Mapeo de campos de Frontend (formData) a la estructura EXACTA de la API
      const bodyData = {
          id_producto: isEditing ? recetaId : 0, 
          codigo_receta: recipeData.codigo_receta || (recipeData.nombre_receta ? recipeData.nombre_receta.toUpperCase().replace(/\s/g, '_').substring(0, 10) : 'REC_NEW'),
          nombre_receta: recipeData.nombre_receta || "",
          descripcion: recipeData.descripcion || "",
          rendimiento_producto_terminado: recipeData.rendimiento_producto_terminado || 1,
          costo_estimado: totalCost, 
          version: recipeData.version || 1,
          estado: recipeData.estado || "ACTIVA", 

          detalles: recipeData.detalles?.map(detail => {
            const ingredientData = availableIngredients.find(a => a.id === detail.id_insumo);
            const costoUnitario = ingredientData?.costPerUnit || 0;

            return {
                id_insumo: detail.id_insumo, 
                cantidad: detail.cantidad,      
                costo_unitario: costoUnitario,
                costo_total: detail.cantidad * costoUnitario, 
                es_opcional: detail.es_opcional, 
                observaciones: detail.observaciones
            }
          }), 
      }

      try {
          const response = await fetch(url, {
              method: method,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(bodyData), 
          });

          if (!response.ok) {
              const errorResult = await response.json();
              throw new Error(errorResult.message || `Error al ${isEditing ? 'actualizar' : 'crear'} la receta.`);
          }
          
          await fetchRecipes(); 
          setIsDialogOpen(false);
          setEditingRecipe(null);
          setFormData({ detalles: [], id_producto: 0, rendimiento_producto_terminado: 1, version: 1, estado: "ACTIVA" }); 
      } catch (error) {
          console.error(`Error during ${method} operation:`, error);
          alert(`Operación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      }
  }

  // --- Lógica del Formulario ---

  useEffect(() => {
      fetchRecipes();
  }, []);

  const filteredRecipes = recipes.filter(recipe => {
    const name = recipe.nombre_receta || "";
    const description = recipe.descripcion || "";
    const code = recipe.codigo_receta || "";
    
    return name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           description.toLowerCase().includes(searchTerm.toLowerCase()) ||
           code.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const addIngredient = () => {
    const newIngredient: RecipeIngredient = {
      id: Date.now() + Math.random(), 
      id_insumo: 0,
      cantidad: 0,
      costo_unitario: 0,
      costo_total: 0,
      es_opcional: false,
      observaciones: "",
      unit: ""
    };
    setFormData(prev => ({
      ...prev,
      detalles: [...(prev.detalles || []), newIngredient]
    }));
  };

  const updateIngredient = (index: number, field: keyof RecipeIngredient, value: any) => {
    const details = [...(formData.detalles || [])];
    const detail = details[index];
    
    if (field === 'id_insumo') {
      const selectedIngredient = availableIngredients.find(ing => ing.id === parseInt(value));
      if (selectedIngredient) {
        const costoUnitario = selectedIngredient.costPerUnit;
        details[index] = {
          ...detail,
          id_insumo: selectedIngredient.id,
          unit: selectedIngredient.unit,
          costo_unitario: costoUnitario,
          costo_total: detail.cantidad * costoUnitario,
        };
      }
    } else if (field === 'cantidad') {
      const newQuantity = parseFloat(value) || 0;
      details[index] = {
        ...detail,
        cantidad: newQuantity,
        costo_total: newQuantity * detail.costo_unitario,
      };
    } else {
      details[index] = {
        ...detail,
        [field]: value
      };
    }
    setFormData(prev => ({ ...prev, detalles: details }));
  };

  const removeIngredient = (index: number) => {
    const details = [...(formData.detalles || [])];
    details.splice(index, 1);
    setFormData(prev => ({ ...prev, detalles: details }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createOrUpdateReceta(formData);
  };

  const handleEdit = (recipe: Recipe) => {
    setEditingRecipe(recipe);
    // Carga los datos mapeados del backend al formulario de frontend
    setFormData(recipe); 
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm("¿Está seguro que desea eliminar esta receta?")) {
      handleDeleteAPI(id);
    }
  };

  const handleDeleteAPI = async (id: number) => { 
      try {
          const response = await fetch(`${RECETAS_API_URL}/${id}`, {
              method: 'DELETE',
          });
          
          if (!response.ok) {
              const errorResult = await response.json();
              throw new Error(errorResult.message || 'Error al eliminar la receta');
          }

          setRecipes(prev => prev.filter(r => r.id !== id));
      } catch (error) {
          console.error("Error deleting recipe:", error);
          alert(`Eliminación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      }
  }; 
  
  const openAddDialog = () => {
    setEditingRecipe(null);
    setFormData({ 
      detalles: [],
      id_producto: 0, // CRÍTICO: Asegurar ID 0 para POST
      nombre_receta: "",
      descripcion: "",
      codigo_receta: "",
      rendimiento_producto_terminado: 1,
      costo_estimado: 0,
      version: 1,
      estado: "ACTIVA",
    });
    setIsDialogOpen(true);
  };


  // --- RENDERIZADO DEL COMPONENTE (Ajustado a tu API) ---
  return (
    <div className="space-y-6">
      {/* Header y Dialog Trigger */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Recetas</h2>
          <p className="text-muted-foreground">Administra las recetas y calcula costos de producción</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Nueva Receta
            </Button>
          </DialogTrigger>
          
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
                  <Label htmlFor="nombre_receta">Nombre de la Receta</Label>
                  <Input
                    id="nombre_receta"
                    placeholder="Ej: Pastel de Chocolate"
                    value={formData.nombre_receta || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, nombre_receta: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="codigo_receta">Código de Receta</Label>
                  <Input
                    id="codigo_receta"
                    placeholder="Ej: PC001"
                    value={formData.codigo_receta || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, codigo_receta: e.target.value }))}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="descripcion">Descripción</Label>
                <Textarea
                  id="descripcion"
                  placeholder="Descripción breve de la receta"
                  value={formData.descripcion || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, descripcion: e.target.value }))}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="rendimiento">Rendimiento (Unidades)</Label>
                  <Input
                    id="rendimiento"
                    type="number"
                    value={formData.rendimiento_producto_terminado || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, rendimiento_producto_terminado: parseInt(e.target.value) }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="version">Versión</Label>
                  <Input
                    id="version"
                    type="number"
                    value={formData.version || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, version: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <Separator />

              {/* Ingredientes (detalles) */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label className="text-base">Insumos (Detalles de la Receta)</Label>
                  <Button type="button" variant="outline" onClick={addIngredient}>
                    <Plus className="h-4 w-4 mr-2" />
                    Agregar Insumo
                  </Button>
                </div>

                {(formData.detalles || []).map((detail, index) => (
                  <div key={detail.id} className="grid grid-cols-1 md:grid-cols-5 gap-4 p-4 border rounded-md">
                    <div className="space-y-2">
                      <Label>Insumo</Label>
                      <Select 
                        value={detail.id_insumo?.toString() || ""} 
                        onValueChange={(value) => updateIngredient(index, 'id_insumo', value)}
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar insumo" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableIngredients.map(ing => (
                            <SelectItem key={ing.id} value={ing.id.toString()}>
                              {ing.name} ({ing.unit})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Cantidad</Label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={detail.cantidad || ""}
                        onChange={(e) => updateIngredient(index, 'cantidad', e.target.value)}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Unidad</Label>
                      <Input
                        value={detail.unit || "N/A"}
                        disabled
                        className="bg-gray-50"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Costo Total</Label>
                      <Input
                        value={`$${detail.costo_total.toFixed(2)}`}
                        disabled
                        className="bg-gray-50 font-medium"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Acción</Label>
                      <Button 
                        type="button" 
                        variant="outline" 
                        size="sm"
                        onClick={() => removeIngredient(index)}
                        className="text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <Separator />

              {/* Costo Estimado (Solo lectura) */}
              <div className="space-y-2">
                <Label>Costo Estimado Total (Se calcula automáticamente)</Label>
                <div className="p-3 bg-gray-50 rounded-md">
                  <p className="text-xl font-bold text-green-700">
                    ${calculateTotalCost().toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Botones de acción */}
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

      {/* Controles de búsqueda */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar recetas por nombre o código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Lista de recetas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recipes.length === 0 ? (
            <p className="col-span-3 text-center text-muted-foreground">Cargando recetas...</p>
        ) : (
            filteredRecipes.map((recipe, index) => (
            <Card 
                key={recipe.id || `recipe-${index}`} 
                className="hover:shadow-lg transition-shadow"
            >
                <CardHeader>
                <div className="flex justify-between items-start">
                    <div className="flex-1">
                    <CardTitle className="text-lg">{recipe.nombre_receta}</CardTitle>
                    <CardDescription>{recipe.descripcion}</CardDescription>
                    </div>
                    <Badge variant="secondary">
                        {recipe.codigo_receta}
                    </Badge>
                </div>
                </CardHeader>
                <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center">
                    <ChefHat className="h-4 w-4 mr-1" />
                    Versión {recipe.version}
                    </div>
                    <div className="flex items-center">
                    <div className={`h-2 w-2 rounded-full ${recipe.estado === 'ACTIVA' ? 'bg-green-500' : 'bg-red-500'} mr-1`}></div>
                    {recipe.estado}
                    </div>
                </div>

                <div className="space-y-2 pt-2">
                    <div className="flex justify-between">
                    <span className="text-sm">Rendimiento (unidades):</span>
                    <span className="font-medium">{recipe.rendimiento_producto_terminado}</span>
                    </div>
                    <div className="flex justify-between">
                    <span className="text-sm font-bold">Costo Estimado Total:</span>
                    <span className="font-bold text-green-700">${(recipe.costo_estimado || 0).toFixed(2)}</span>
                    </div>
                </div>

                <div className="flex space-x-2 pt-2">
                    <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(recipe)}
                    className="flex-1"
                    >
                    <Edit className="h-3 w-3 mr-1" />
                    Editar
                    </Button>
                    <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(recipe.id)}
                    className="text-red-600 hover:text-red-700"
                    >
                    <Trash2 className="h-3 w-3" />
                    </Button>
                </div>
                </CardContent>
            </Card>
            ))
        )}
      </div>
    </div>
  );
}