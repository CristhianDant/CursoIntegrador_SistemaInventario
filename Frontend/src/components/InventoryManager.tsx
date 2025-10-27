import { useState, useEffect } from "react";
import { Plus, Search, Filter, Edit, Trash2, Package } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { API_BASE_URL } from "../constants";

interface Ingredient {
  id: number;
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  unit: string;
  costPerUnit: number;
  supplier: string;
  expiryDate: string;
  location: string;
  notes?: string;
}



const categories = ["Harinas", "Endulzantes", "Proteínas", "Lácteos", "Chocolates", "Frutas", "Especias"];

export function InventoryManager() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);
  const [formData, setFormData] = useState<Partial<Ingredient>>({});

  const fetchIngredients = async () => {
    try {
        // 🚨 CAMBIO CRÍTICO: De '/v1/insumo/' a '/v1/insumos/' (Asegúrate que API_BASE_URL no termine en '/')
        const response = await fetch(`${API_BASE_URL}/v1/insumos/`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            // Se actualiza el manejo de error para ser más informativo
            const errorText = await response.text();
            throw new Error(`Error al cargar insumos: ${response.statusText}. Respuesta del servidor: ${errorText}`);
        }

        const responseData = await response.json();
        
        if (responseData.success && Array.isArray(responseData.data)) {
            
            // EL MAPEO DE DATOS (sigue siendo el mismo, de snake_case a camelCase)
            const loadedIngredients: Ingredient[] = responseData.data.map((p: any) => ({
                id: p.id_insumo,                   
                name: p.nombre,                     
                currentStock: parseFloat(p.stock_actual || 0), 
                minStock: parseFloat(p.stock_minimo || 0),   
                unit: p.unidad_medida,              
                costPerUnit: parseFloat(p.precio_promedio || 0), 
                category: p.categoria || "N/A",     
                notes: p.descripcion || "",       
                supplier: "N/A (Cargar luego)",
                location: "N/A (Cargar luego)",
                expiryDate: "2999-12-31", 
            })) as Ingredient[];
            
            setIngredients(loadedIngredients);
        }

    } catch (error) {
        console.error("Fallo la conexión con el Backend:", error);
    }
};



  const filteredIngredients = ingredients.filter(ingredient => {
    const matchesSearch = ingredient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ingredient.supplier.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || ingredient.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStockStatus = (ingredient: Ingredient) => {
    const daysUntilExpiry = Math.ceil((new Date(ingredient.expiryDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    
    // Prioridad: 1. Stock bajo, 2. Por vencer (crítico), 3. Por vencer (advertencia)
    if (ingredient.currentStock <= ingredient.minStock) return { label: "Stock Bajo", variant: "secondary" as const };
    if (daysUntilExpiry <= 3 && daysUntilExpiry >= 0) return { label: "Por Vencer", variant: "destructive" as const };
    if (daysUntilExpiry <= 7 && daysUntilExpiry >= 0) return { label: "Por Vencer", variant: "outline" as const };
    if (daysUntilExpiry < 0) return { label: "Revisar Fecha", variant: "destructive" as const }; // Para fechas pasadas, pero sin usar "Vencido"
    return { label: "Normal", variant: "default" as const };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingIngredient) {
      setIngredients(prev => 
        prev.map(ingredient => 
          ingredient.id === editingIngredient.id 
            ? { ...ingredient, ...formData }
            : ingredient
        )
      );
    } else {
      const newIngredient: Ingredient = {
        id: Math.max(...ingredients.map(i => i.id)) + 1,
        ...formData as Ingredient
      };
      setIngredients(prev => [...prev, newIngredient]);
    }
    
    setIsDialogOpen(false);
    setEditingIngredient(null);
    setFormData({});
  };

  const handleEdit = (ingredient: Ingredient) => {
    setEditingIngredient(ingredient);
    setFormData(ingredient);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    setIngredients(prev => prev.filter(ingredient => ingredient.id !== id));
  };

  const openAddDialog = () => {
    setEditingIngredient(null);
    setFormData({});
    setIsDialogOpen(true);
  };

  
  // 2. LLAMADA AL EFECTO
  // Esto debe ir después de la definición de fetchIngredients
  useEffect(() => {
    fetchIngredients();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header y controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Inventario</h2>
          <p className="text-muted-foreground">Administra todos los insumos de tu pastelería</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Agregar Insumo
            </Button>
          </DialogTrigger>
          
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingIngredient ? "Editar Insumo" : "Agregar Nuevo Insumo"}
              </DialogTitle>
              <DialogDescription>
                {editingIngredient ? "Modifica la información del insumo" : "Completa los datos del nuevo insumo"}
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nombre del Insumo</Label>
                  <Input
                    id="name"
                    placeholder="Ej: Harina de trigo"
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
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="currentStock">Stock Actual</Label>
                  <Input
                    id="currentStock"
                    type="number"
                    placeholder="25"
                    value={formData.currentStock || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, currentStock: parseFloat(e.target.value) }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="minStock">Stock Mínimo</Label>
                  <Input
                    id="minStock"
                    type="number"
                    placeholder="10"
                    value={formData.minStock || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, minStock: parseFloat(e.target.value) }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="unit">Unidad</Label>
                  <Select 
                    value={formData.unit || ""} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, unit: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Unidad" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="kg">Kilogramos</SelectItem>
                      <SelectItem value="g">Gramos</SelectItem>
                      <SelectItem value="litros">Litros</SelectItem>
                      <SelectItem value="ml">Mililitros</SelectItem>
                      <SelectItem value="unidades">Unidades</SelectItem>
                      <SelectItem value="docenas">Docenas</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="costPerUnit">Costo por Unidad</Label>
                  <Input
                    id="costPerUnit"
                    type="number"
                    step="0.01"
                    placeholder="1.50"
                    value={formData.costPerUnit || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, costPerUnit: parseFloat(e.target.value) }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="expiryDate">Fecha de Vencimiento</Label>
                  <Input
                    id="expiryDate"
                    type="date"
                    value={formData.expiryDate || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, expiryDate: e.target.value }))}
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="supplier">Proveedor</Label>
                  <Input
                    id="supplier"
                    placeholder="Molinos ABC"
                    value={formData.supplier || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, supplier: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="location">Ubicación</Label>
                  <Input
                    id="location"
                    placeholder="Almacén A - Estante 1"
                    value={formData.location || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="notes">Notas Adicionales</Label>
                <Textarea
                  id="notes"
                  placeholder="Notas opcionales sobre el insumo..."
                  value={formData.notes || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                />
              </div>
              
              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {editingIngredient ? "Actualizar" : "Agregar"}
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
                placeholder="Buscar por nombre o proveedor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="h-4 w-4 mr-2" />
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

      {/* Tabla de inventario */}
      <Card>
        <CardHeader>
          <CardTitle>Inventario Actual</CardTitle>
          <CardDescription>
            {filteredIngredients.length} insumos encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Insumo</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Vencimiento</TableHead>
                  <TableHead>Costo</TableHead>
                  <TableHead>Proveedor</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredIngredients.map((ingredient) => {
                  const status = getStockStatus(ingredient);
                  const daysUntilExpiry = Math.ceil((new Date(ingredient.expiryDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                  
                  return (
                    <TableRow key={ingredient.id}>
                      <TableCell className="font-medium">{ingredient.name}</TableCell>
                      <TableCell>{ingredient.category}</TableCell>
                      <TableCell>
                        {ingredient.currentStock} {ingredient.unit}
                        <br />
                        <span className="text-xs text-muted-foreground">
                          Min: {ingredient.minStock} {ingredient.unit}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={status.variant}>{status.label}</Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(ingredient.expiryDate).toLocaleDateString()}
                        <br />
                        <span className={`text-xs ${
                          daysUntilExpiry <= 3 && daysUntilExpiry >= 0 ? 'text-red-600' : 
                          daysUntilExpiry <= 7 && daysUntilExpiry >= 0 ? 'text-orange-600' : 
                          daysUntilExpiry < 0 ? 'text-red-800' : 'text-muted-foreground'
                        }`}>
                          {daysUntilExpiry >= 0 ? `${daysUntilExpiry} días restantes` : 'Fecha pasada - Revisar'}
                        </span>
                      </TableCell>
                      <TableCell>
                        ${ingredient.costPerUnit.toFixed(2)}
                        <br />
                        <span className="text-xs text-muted-foreground">
                          Total: ${(ingredient.currentStock * ingredient.costPerUnit).toFixed(2)}
                        </span>
                      </TableCell>
                      <TableCell>{ingredient.supplier}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(ingredient)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(ingredient.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}