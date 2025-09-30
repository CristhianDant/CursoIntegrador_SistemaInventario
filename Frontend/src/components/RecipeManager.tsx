import { useState } from "react";
import { Plus, Search, Edit, Trash2, ChefHat, Clock, Users } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Separator } from "./ui/separator";

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

// Mock data de insumos disponibles
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

const mockRecipes: Recipe[] = [
  {
    id: 1,
    name: "Pastel de Chocolate Clásico",
    description: "Delicioso pastel de chocolate húmedo con glaseado",
    category: "Pasteles",
    preparationTime: 30,
    cookingTime: 45,
    servings: 8,
    difficulty: 'Intermedio',
    instructions: "1. Precalentar horno a 180°C...",
    ingredients: [
      { id: 1, ingredientId: 1, ingredientName: "Harina de trigo", quantity: 0.5, unit: "kg", cost: 0.6 },
      { id: 2, ingredientId: 2, ingredientName: "Azúcar refinada", quantity: 0.3, unit: "kg", cost: 0.75 },
      { id: 3, ingredientId: 3, ingredientName: "Huevos frescos", quantity: 4, unit: "unidades", cost: 1.32 },
      { id: 4, ingredientId: 6, ingredientName: "Chocolate negro 70%", quantity: 0.2, unit: "kg", cost: 3.0 },
    ],
    totalCost: 5.67,
    costPerServing: 0.71,
    profit: 65,
    sellingPrice: 12.0
  },
  {
    id: 2,
    name: "Galletas de Mantequilla",
    description: "Clásicas galletas crujientes de mantequilla",
    category: "Galletas",
    preparationTime: 20,
    cookingTime: 15,
    servings: 24,
    difficulty: 'Fácil',
    instructions: "1. Batir mantequilla con azúcar...",
    ingredients: [
      { id: 1, ingredientId: 1, ingredientName: "Harina de trigo", quantity: 0.25, unit: "kg", cost: 0.3 },
      { id: 2, ingredientId: 4, ingredientName: "Mantequilla", quantity: 0.15, unit: "kg", cost: 1.28 },
      { id: 3, ingredientId: 2, ingredientName: "Azúcar refinada", quantity: 0.1, unit: "kg", cost: 0.25 },
    ],
    totalCost: 1.83,
    costPerServing: 0.08,
    profit: 200,
    sellingPrice: 0.25
  }
];

const categories = ["Pasteles", "Galletas", "Panes", "Postres", "Decoraciones"];

export function RecipeManager() {
  const [recipes, setRecipes] = useState<Recipe[]>(mockRecipes);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  const [formData, setFormData] = useState<Partial<Recipe>>({
    ingredients: []
  });

  const filteredRecipes = recipes.filter(recipe => {
    const matchesSearch = recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         recipe.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || recipe.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const addIngredient = () => {
    const newIngredient: RecipeIngredient = {
      id: Date.now(),
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const totalCost = calculateTotalCost();
    const costPerServing = totalCost / (formData.servings || 1);
    
    if (editingRecipe) {
      setRecipes(prev => 
        prev.map(recipe => 
          recipe.id === editingRecipe.id 
            ? { 
                ...recipe, 
                ...formData,
                totalCost,
                costPerServing,
                profit: formData.sellingPrice ? ((formData.sellingPrice - costPerServing) / costPerServing) * 100 : 0
              } as Recipe
            : recipe
        )
      );
    } else {
      const newRecipe: Recipe = {
        id: Math.max(...recipes.map(r => r.id)) + 1,
        ...formData,
        totalCost,
        costPerServing,
        profit: formData.sellingPrice ? ((formData.sellingPrice - costPerServing) / costPerServing) * 100 : 0
      } as Recipe;
      setRecipes(prev => [...prev, newRecipe]);
    }
    
    setIsDialogOpen(false);
    setEditingRecipe(null);
    setFormData({ ingredients: [] });
  };

  const handleEdit = (recipe: Recipe) => {
    setEditingRecipe(recipe);
    setFormData(recipe);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    setRecipes(prev => prev.filter(recipe => recipe.id !== id));
  };

  const openAddDialog = () => {
    setEditingRecipe(null);
    setFormData({ ingredients: [] });
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
      {/* Header */}
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
              {/* Información básica */}
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
                    onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
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

              {/* Detalles de tiempo y dificultad */}
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
                    onValueChange={(value) => setFormData(prev => ({ ...prev, difficulty: value as Recipe['difficulty'] }))}
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

              {/* Ingredientes */}
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
                        onValueChange={(value) => updateIngredient(index, 'ingredientId', value)}
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

                {(formData.ingredients || []).length > 0 && (
                  <div className="flex justify-end">
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Costo Total de Ingredientes</p>
                      <p className="text-lg font-semibold">${calculateTotalCost().toFixed(2)}</p>
                      <p className="text-sm text-muted-foreground">
                        Costo por porción: ${(calculateTotalCost() / (formData.servings || 1)).toFixed(2)}
                      </p>
                    </div>
                  </div>
                )}
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

              {/* Instrucciones */}
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
        {filteredRecipes.map((recipe) => (
          <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
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
                  <span className="font-medium">${recipe.totalCost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Costo por porción:</span>
                  <span className="font-medium">${recipe.costPerServing.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Precio de venta:</span>
                  <span className="font-medium">${recipe.sellingPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Margen:</span>
                  <span className={`font-medium ${recipe.profit > 50 ? 'text-green-600' : recipe.profit > 20 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {recipe.profit.toFixed(1)}%
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
        ))}
      </div>
    </div>
  );
}