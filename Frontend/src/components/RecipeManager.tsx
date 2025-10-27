import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, ChefHat, Clock, Users } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";

// Importación de la constante de la API (Asegúrate de que exista en tu archivo constants.ts)
// Nota: Usamos una URL de ejemplo si no está disponible la constante
const API_BASE_URL = "http://localhost:8000/api"; 


// --- CONFIGURACIÓN DE URL UNIFICADA ---
const RECETAS_API_URL = `${API_BASE_URL}/v1/recetas/`; 
// --------------------------------------

interface RecipeIngredient {
  id: number;
  ingredientId: number;
  ingredientName: string;
  quantity: number;
  unit: string;
  cost: number;
}

interface Recipe {
  id: number;
  name: string;
  description: string;
  category: string;
  preparationTime: number;
  cookingTime: number;
  servings: number;
  difficulty: 'Fácil' | 'Intermedio' | 'Difícil';
  instructions: string;
  ingredients: RecipeIngredient[];
  totalCost: number;
  costPerServing: number;
  profit: number;
  sellingPrice: number;
}

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

const categories = ["Pasteles", "Galletas", "Panes", "Postres", "Decoraciones"];

export function RecipeManager() {
  const [recipes, setRecipes] = useState<Recipe[]>([]); 
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  const [formData, setFormData] = useState<Partial<Recipe>>({
    ingredients: []
  });

  // --- Funciones API ---

  const fetchRecipes = async () => {
    try {
        const response = await fetch(RECETAS_API_URL, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) {
            throw new Error('Error al cargar las recetas');
        }
        
        const result = await response.json();
        const rawRecipes = result.data || result || [];

        // ***** INICIO DE LA CORRECCIÓN DE MAPEO *****
        const mappedRecipes: Recipe[] = rawRecipes.map((r: any) => {
            // Asumiendo que el backend retorna:
            // id_receta, nombre_receta, descripcion, tiempo_preparacion, etc.
            
            const totalCost = Number(r.costo_total || r.costo_estimado || 0);
            const servings = Number(r.rendimiento_porciones || r.rendimiento_producto_terminado || 1);
            const costPerServing = Number(r.costo_por_porcion) || (servings ? totalCost / servings : 0);
            const sellingPrice = Number(r.precio_venta || r.sellingPrice || 0);
            const profit = sellingPrice && costPerServing ? ((sellingPrice - costPerServing) / costPerServing) * 100 : 0;
            
            return {
                // Mapeo de campos esenciales (Título y Descripción)
                id: r.id_receta || r.id, 
                name: r.nombre_receta || r.nombre || r.name || "Receta sin Título", // Usar r.nombre_receta o r.nombre
                description: r.descripcion || r.description || "Receta sin Descripción", // Usar r.descripcion
                
                // Mapeo de campos de tiempo y cantidad
                preparationTime: Number(r.tiempo_preparacion) || 0,
                cookingTime: Number(r.tiempo_coccion) || 0,
                servings: servings, 
                
                // Mapeo de otros campos
                category: r.categoria || r.category || categories[0],
                difficulty: r.dificultad || r.difficulty || 'Fácil',
                instructions: r.instrucciones || r.instructions || '',
                ingredients: r.ingredientes || r.ingredients || [],
                
                // Mapeo de costos calculados (para visualización)
                totalCost: totalCost, 
                costPerServing: costPerServing,
                sellingPrice: sellingPrice,
                profit: profit,
            } as Recipe;
        });
        // ***** FIN DE LA CORRECCIÓN DE MAPEO *****
        
        setRecipes(mappedRecipes); 
    } catch (error) {
        console.error("Error fetching recipes:", error);
    }
  };

  const createOrUpdateReceta = async (recipeData: Partial<Recipe>) => {
      const isEditing = recipeData.id && recipeData.id !== 0;
      const url = isEditing ? `${RECETAS_API_URL}${recipeData.id}` : RECETAS_API_URL;
      const method = isEditing ? 'PUT' : 'POST';

      const totalCost = calculateTotalCost();
      const servings = recipeData.servings || 1;
      const costPerServing = totalCost / servings;
      const sellingPrice = recipeData.sellingPrice || 0;
      const profit = sellingPrice ? ((sellingPrice - costPerServing) / costPerServing) * 100 : 0;

      // Aquí deberías transformar los nombres de campo de vuelta 
      // a la estructura que espera tu backend (ej: name -> nombre_receta)
      const bodyData = {
          // Si el backend espera nombre_receta y descripcion, envíalos así:
          nombre_receta: recipeData.name, 
          descripcion: recipeData.description,
          
          // Otros campos:
          categoria: recipeData.category,
          tiempo_preparacion: Number(recipeData.preparationTime) || 0,
          tiempo_coccion: Number(recipeData.cookingTime) || 0,
          rendimiento_porciones: servings, // o el nombre que use tu BD
          precio_venta: sellingPrice,
          dificultad: recipeData.difficulty,
          instrucciones: recipeData.instructions,
          
          // La lista de ingredientes puede requerir mapeo también:
          ingredientes: recipeData.ingredients?.map(ing => ({
            id_insumo: ing.ingredientId, // asumiendo que tu BD usa 'id_insumo'
            cantidad: ing.quantity,
            // ... otros campos de ingrediente
          })) 
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
          setFormData({ ingredients: [] });
      } catch (error) {
          console.error(`Error during ${method} operation:`, error);
          alert(`Operación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      }
  }
  
  const handleDeleteAPI = async (id: number) => { 
      try {
          // Corregir la URL para asegurar que la barra (/) esté presente si es necesario
          const response = await fetch(`${RECETAS_API_URL}${id}`, {
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
  
  useEffect(() => {
      fetchRecipes();
  }, []);

  // Filtrado de recetas (Corrección del TypeError incluida)
  const filteredRecipes = recipes.filter(recipe => {
    // Usamos el operador || "" para asegurar que siempre sea un string antes de toLowerCase()
    const recipeName = recipe.name || "";
    const recipeDescription = recipe.description || "";
    
    const matchesSearch = recipeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         recipeDescription.toLowerCase().includes(searchTerm.toLowerCase());
                         
    const matchesCategory = selectedCategory === "all" || recipe.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // ... (Resto de funciones: addIngredient, updateIngredient, removeIngredient, etc. no han cambiado)
  
  const addIngredient = () => {
    const newIngredient: RecipeIngredient = {
      // Usar Date.now() + Math.random() para asegurar un ID único en el frontend
      id: Date.now() + Math.random(), 
      ingredientId: 0,
      ingredientName: "",
      quantity: 0,
      unit: "",
      cost: 0
    };
    setFormData(prev => ({
      ...prev,
      ingredients: [...(prev.ingredients || []), newIngredient]
    }));
  };

  const updateIngredient = (index: number, field: keyof RecipeIngredient, value: any) => {
    const ingredients = [...(formData.ingredients || [])];
    if (field === 'ingredientId') {
      const selectedIngredient = availableIngredients.find(ing => ing.id === parseInt(value));
      if (selectedIngredient) {
        ingredients[index] = {
          ...ingredients[index],
          ingredientId: selectedIngredient.id,
          ingredientName: selectedIngredient.name,
          unit: selectedIngredient.unit,
          cost: ingredients[index].quantity * selectedIngredient.costPerUnit
        };
      }
    } else if (field === 'quantity') {
      const ingredient = availableIngredients.find(ing => ing.id === ingredients[index].ingredientId);
      ingredients[index] = {
        ...ingredients[index],
        [field]: parseFloat(value) || 0,
        cost: ingredient ? (parseFloat(value) || 0) * ingredient.costPerUnit : 0
      };
    } else {
      ingredients[index] = {
        ...ingredients[index],
        [field]: value
      };
    }
    setFormData(prev => ({ ...prev, ingredients }));
  };

  const removeIngredient = (index: number) => {
    const ingredients = [...(formData.ingredients || [])];
    ingredients.splice(index, 1);
    setFormData(prev => ({ ...prev, ingredients }));
  };

  const calculateTotalCost = () => {
    return (formData.ingredients || []).reduce((total, ing) => total + ing.cost, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createOrUpdateReceta(formData);
  };

  const handleEdit = (recipe: Recipe) => {
    setEditingRecipe(recipe);
    setFormData(recipe);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm("¿Está seguro que desea eliminar esta receta?")) {
      handleDeleteAPI(id);
    }
  };

  const openAddDialog = () => {
    setEditingRecipe(null);
    setFormData({ 
      ingredients: [],
      name: "",
      description: "",
      category: categories[0],
      difficulty: 'Fácil',
      preparationTime: 0,
      cookingTime: 0,
      servings: 1,
      sellingPrice: 0,
    });
    setIsDialogOpen(true);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Fácil': return 'bg-green-100 text-green-800';
      case 'Intermedio': return 'bg-yellow-100 text-yellow-800';
      case 'Difícil': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

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
                {editingRecipe ? "Modifica la información de la receta" : "Crea una nueva receta con ingredientes y costos"}
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Información básica y detalles */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nombre de la Receta</Label>
                  <Input
                    id="name"
                    placeholder="Ej: Pastel de Chocolate"
                    value={formData.name || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="category">Categoría</Label>
                  <Select 
                    value={formData.category || ""} 
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, category: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona categoría" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(category => (
                        <SelectItem key={category} value={category}>{category}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descripción</Label>
                <Textarea
                  id="description"
                  placeholder="Descripción breve de la receta"
                  value={formData.description || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="prepTime">Prep. (min)</Label>
                  <Input
                    id="prepTime"
                    type="number"
                    value={formData.preparationTime || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, preparationTime: parseInt(e.target.value) }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="cookTime">Cocción (min)</Label>
                  <Input
                    id="cookTime"
                    type="number"
                    value={formData.cookingTime || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, cookingTime: parseInt(e.target.value) }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="servings">Porciones</Label>
                  <Input
                    id="servings"
                    type="number"
                    value={formData.servings || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, servings: parseInt(e.target.value) }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="difficulty">Dificultad</Label>
                  <Select 
                    value={formData.difficulty || ""} 
                    onValueChange={(value: string) => setFormData(prev => ({ ...prev, difficulty: value as Recipe['difficulty'] }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Dificultad" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Fácil">Fácil</SelectItem>
                      <SelectItem value="Intermedio">Intermedio</SelectItem>
                      <SelectItem value="Difícil">Difícil</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              {/* Ingredientes (Con key única garantizada) */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label className="text-base">Ingredientes</Label>
                  <Button type="button" variant="outline" onClick={addIngredient}>
                    <Plus className="h-4 w-4 mr-2" />
                    Agregar Ingrediente
                  </Button>
                </div>

                {(formData.ingredients || []).map((ingredient, index) => (
                  <div key={ingredient.id} className="grid grid-cols-1 md:grid-cols-5 gap-4 p-4 border rounded-md">
                    <div className="space-y-2">
                      <Label>Ingrediente</Label>
                      <Select 
                        value={ingredient.ingredientId?.toString() || ""} 
                        onValueChange={(value: string) => updateIngredient(index, 'ingredientId', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableIngredients.map(ing => (
                            <SelectItem key={ing.id} value={ing.id.toString()}>
                              {ing.name} ({ing.currentStock} {ing.unit})
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
                        placeholder="0"
                        value={ingredient.quantity || ""}
                        onChange={(e) => updateIngredient(index, 'quantity', e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Unidad</Label>
                      <Input
                        value={ingredient.unit || ""}
                        disabled
                        className="bg-gray-50"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Costo</Label>
                      <Input
                        value={`$${ingredient.cost.toFixed(2)}`}
                        disabled
                        className="bg-gray-50"
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

              {/* Precio y rentabilidad */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="sellingPrice">Precio de Venta por Porción</Label>
                  <Input
                    id="sellingPrice"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={formData.sellingPrice || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, sellingPrice: parseFloat(e.target.value) }))}
                  />
                </div>
                
                {formData.sellingPrice && formData.servings && (
                  <div className="space-y-2">
                    <Label>Margen de Ganancia</Label>
                    <div className="p-3 bg-green-50 rounded-md">
                      <p className="text-sm text-green-700">
                        Ganancia: {(((formData.sellingPrice - (calculateTotalCost() / formData.servings)) / (calculateTotalCost() / formData.servings)) * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Instrucciones y botones de acción */}
              <div className="space-y-2">
                <Label htmlFor="instructions">Instrucciones de Preparación</Label>
                <Textarea
                  id="instructions"
                  placeholder="Paso a paso para preparar la receta..."
                  value={formData.instructions || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
                  rows={6}
                />
              </div>
              
              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {editingRecipe ? "Actualizar" : "Crear Receta"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Controles de búsqueda y filtrado */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar recetas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Todas las categorías" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las categorías</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Lista de recetas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recipes.length === 0 ? (
            <p className="col-span-3 text-center text-muted-foreground">Cargando recetas o ninguna receta encontrada...</p>
        ) : (
            filteredRecipes.map((recipe, index) => (
            <Card 
                key={recipe.id || `recipe-${index}`} 
                className="hover:shadow-lg transition-shadow"
            >
                <CardHeader>
                <div className="flex justify-between items-start">
                    <div className="flex-1">
                    {/* Aquí ahora se usan los campos mapeados: recipe.name y recipe.description */}
                    <CardTitle className="text-lg">{recipe.name}</CardTitle>
                    <CardDescription>{recipe.description}</CardDescription>
                    </div>
                    <Badge className={getDifficultyColor(recipe.difficulty)}>
                    {recipe.difficulty}
                    </Badge>
                </div>
                </CardHeader>
                <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {recipe.preparationTime + recipe.cookingTime} min
                    </div>
                    <div className="flex items-center">
                    <Users className="h-4 w-4 mr-1" />
                    {recipe.servings} porciones
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between">
                    <span className="text-sm">Costo total:</span>
                    <span className="font-medium">${(recipe.totalCost || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                    <span className="text-sm">Costo por porción:</span>
                    <span className="font-medium">${(recipe.costPerServing || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                    <span className="text-sm">Precio de venta:</span>
                    <span className="font-medium">${(recipe.sellingPrice || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                    <span className="text-sm">Margen:</span>
                    <span className={`font-medium ${(recipe.profit || 0) > 50 ? 'text-green-600' : (recipe.profit || 0) > 20 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {(recipe.profit || 0).toFixed(1)}%
                    </span>
                    </div>
                </div>

                <div className="flex space-x-2">
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