import { useState, useEffect } from "react";
import { Plus, Search, Filter, Edit, Trash2, Package } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "../context/AuthContext";
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
  //Añadir 'code' (código es un VARCHAR en el modelo)
  code: string; 
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  unit: string;
  costPerUnit: number; // Se mantiene, pero se omite en la UI
  // supplier, isPerishable, location se manejan como opcionales
  notes?: string;
  // Se añaden los campos opcionales para evitar errores si la lógica los usa:
  supplier?: string; 
  isPerishable?: boolean;
  location?: string;
}



const categories = ["Harinas", "Endulzantes", "Proteínas", "Lacteos", "Chocolates", "Frutas", "Especias"];

export function InventoryManager() {
  const { canWrite } = useAuth();
  const canEditInsumos = canWrite('INSUMOS');
  
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);
  const [formData, setFormData] = useState<Partial<Ingredient>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

const fetchIngredients = async () => {
    try {
        //CAMBIO CRÍTICO: De '/v1/insumo/' a '/v1/insumos/' (Asegúrate que API_BASE_URL no termine en '/')
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
        
        const loadedIngredients: Ingredient[] = responseData.data.map((p: any) => ({
        id: p.id_insumo,                   
        name: p.nombre,                     
        // USAR p.codigo para el campo 'code'
        code: p.codigo, 
        currentStock: parseFloat(p.stock_actual || 0), 
        minStock: parseFloat(p.stock_minimo || 0),   
        unit: p.unidad_medida,              
        costPerUnit: parseFloat(p.precio_promedio || 0), 
        category: p.categoria || "N/A",     
        notes: p.descripcion || "", 
        isPerishable: !!p.perecible,     
    })) as Ingredient[];
            
            setIngredients(loadedIngredients);
    } catch (error) {
        console.error("Fallo la conexión con el Backend:", error);
    }
};

const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea eliminar este insumo?")) return;
    try {
        // 🛑 RUTA DELETE /insumos/{id}
        const response = await fetch(`${API_BASE_URL}/v1/insumos/${id}`, { 
            method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Error al eliminar');
        
        // Si la eliminación fue exitosa en el backend:
        setIngredients(ingredients.filter(i => i.id !== id));
        alert("Insumo eliminado exitosamente.");
    } catch (error) {
        console.error("Error al eliminar el insumo:", error);
        alert("Error al eliminar el insumo.");
    }
};

const handleEdit = (ingredient: Ingredient) => {
    setEditingIngredient(ingredient); // Marca qué insumo estamos editando
    setFormData(ingredient);          // Carga los datos en el formulario
    setIsDialogOpen(true);            // Abre el modal
};

const openAddDialog = () => {
    setEditingIngredient(null);
    // Asegurarse de que el formulario se inicialice correctamente (ej. con un objeto vacío o valores por defecto)
    setFormData({}); 
    setIsDialogOpen(true);
  };

// --- Encargado de post y put ---

// NOTA: Asegúrate de que tu interfaz Ingredient use 'id: number' o 'id_insumo: number'
// Usaremos 'id' para esta corrección, ya que es el nombre de la interfaz inicial.

const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const isEditing = !!editingIngredient;

    // 1. Parseo seguro de stock_minimo ANTES de enviar
    const minStockValue = formData.minStock 
        ? parseFloat(formData.minStock as any) 
        : 0; 

    // 🛑 OBJETO dataToSend ESTRICTO:
    const dataToSend = {
        // CAMPOS OBLIGATORIOS
        codigo: formData.code,
        nombre: formData.name,
        // FIX: Si está vacío, enviamos "" para que el backend lo fuerce
        // a seleccionar un valor (ya que "" no es un valor de Enum válido).
        unidad_medida: formData.unit || "", 
        
        // CAMPOS OPCIONALES
        descripcion: formData.notes || null, 
        stock_minimo: minStockValue, 
        perecible: !!formData.isPerishable, 
        categoria: formData.category || null, 
    };

    try {
        let url = `${API_BASE_URL}/v1/insumos/`;
        let method = 'POST';
        
        // 🔑 FIX CRÍTICO DEL PUT: Obtener el ID correctamente
        let insumoId;
        if (isEditing) {
            // Obtener el ID de formData (que ya tiene todos los datos del ingrediente)
            insumoId = (formData as Ingredient).id || (editingIngredient as Ingredient)?.id; 
            
            if (!insumoId) {
                 throw new Error("ID de insumo faltante para la operación de actualización. Revisa el estado 'editingIngredient'.");
            }
            
            url = `${API_BASE_URL}/v1/insumos/${insumoId}`;
            method = 'PUT';
        }

        console.log(`[${method}] URL: ${url}`);
        console.log("JSON de la solicitud:", JSON.stringify(dataToSend, null, 2));

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToSend), 
        });

        if (!response.ok) {
            const errorBody = await response.json();
            console.error("Detalles del Error del Servidor (JSON de Pydantic):", errorBody);
            
            const errorMessage = errorBody.detail 
                ? JSON.stringify(errorBody.detail, null, 2)
                : response.statusText;
            
            throw new Error(`Fallo en la operación: ${response.statusText} - Detalles: ${errorMessage}`);
        }
        
        // Lógica de éxito: Actualiza la lista sin refrescar la página
        const responseData = await response.json();
        
        if (isEditing) {
            // Actualiza el insumo en la lista
            const updatedIngredient: Ingredient = {
                id: (editingIngredient as Ingredient).id,
                code: formData.code || "",
                name: formData.name || "",
                category: formData.category || "N/A",
                currentStock: parseFloat(formData.currentStock as any) || 0,
                minStock: parseFloat(formData.minStock as any) || 0,
                unit: formData.unit || "",
                costPerUnit: parseFloat(formData.costPerUnit as any) || 0,
                notes: formData.notes,
                isPerishable: formData.isPerishable,
            };
            setIngredients(ingredients.map(i => i.id === updatedIngredient.id ? updatedIngredient : i));
        } else {
            // Agrega el nuevo insumo a la lista
            const newIngredient: Ingredient = {
                id: responseData.id_insumo || responseData.id,
                code: formData.code || "",
                name: formData.name || "",
                category: formData.category || "N/A",
                currentStock: parseFloat(formData.currentStock as any) || 0,
                minStock: parseFloat(formData.minStock as any) || 0,
                unit: formData.unit || "",
                costPerUnit: parseFloat(formData.costPerUnit as any) || 0,
                notes: formData.notes,
                isPerishable: formData.isPerishable,
            };
            setIngredients([...ingredients, newIngredient]);
        }
        
        setIsDialogOpen(false);
        setFormData({});
        setEditingIngredient(null);
        
        // Mostrar mensaje de éxito
        const message = isEditing ? "Insumo actualizado exitosamente" : "Insumo creado exitosamente";
        setSuccessMessage(message);
        setTimeout(() => setSuccessMessage(null), 3000); 
        
    } catch (error) {
        console.error(`Error al ${isEditing ? 'actualizar' : 'crear'} el insumo:`, error);
        alert(`Error al ${isEditing ? 'actualizar' : 'crear'} el insumo. Revisa la consola para detalles.`);
    }
};

  const filteredIngredients = ingredients.filter(ingredient => {
    const matchesSearch = ingredient.name.toLowerCase().includes(searchTerm.toLowerCase()) 
    const matchesCategory = selectedCategory === "all" || ingredient.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStockStatus = (ingredient: Ingredient) => {
    
    // 1. Condición CRÍTICA (Stock Bajo/Agotado)
    if (ingredient.currentStock <= ingredient.minStock) {
        return { label: "Stock Bajo", variant: "destructive" as const }; 
    }
    
    // 2. Condición de ADVERTENCIA (Cerca del Mínimo)
    // Definimos "Cerca del Mínimo" si el stock es <= 1.5 veces el stock mínimo
    if (ingredient.currentStock <= ingredient.minStock * 1.5) {
        return { label: "Cerca del Mínimo", variant: "warning" as const }; // Usamos 'warning' para amarillo/naranja
    }
    
    // 3. Condición NORMAL
    return { label: "Normal", variant: "default" as const };
};

  
  // 2. LLAMADA AL EFECTO
  // Esto debe ir después de la definición de fetchIngredients
  useEffect(() => {
    fetchIngredients();
  }, []);

  const isFormValid = formData.code?.trim() !== "" && 
                      formData.name?.trim() !== "" && 
                      formData.unit?.trim() !== "";

  return (
    <div className="space-y-6">
      {/* Mensaje de éxito */}
      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg animate-in fade-in slide-in-from-top-2 duration-300">
          {successMessage}
        </div>
      )}
      
      {/* Header y controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Insumos</h2>
          <p className="text-muted-foreground">Administra todos los insumos de tu pastelería</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          {canEditInsumos && (
            <DialogTrigger asChild>
              <Button onClick={openAddDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Agregar Insumo
              </Button>
            </DialogTrigger>
          )}
          
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
      {/* Código (codigo) */}
      <div className="space-y-2">
        <Label htmlFor="code">Código del Insumo *</Label>
        <Input
          id="code"
          placeholder="Ej: HRN001"
          value={formData.code || ""} // FIX: Prevenir advertencia de React
          onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
          required
        />
      </div>

      {/* Nombre (nombre) */}
      <div className="space-y-2">
        <Label htmlFor="name">Nombre del Insumo *</Label>
        <Input
          id="name"
          placeholder="Ej: Harina de trigo"
          value={formData.name || ""} // FIX: Prevenir advertencia de React
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          required
        />
      </div>

      {/* ✅ Categoría (categoria) */}
      <div className="space-y-2">
        <Label htmlFor="category">Categoría</Label>
        <Select 
          // FIX: Usar category y prevenir advertencia de React
          value={formData.category || ""} 
          onValueChange={(value) => setFormData({ ...formData, category: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Selecciona categoría" />
          </SelectTrigger>
          <SelectContent>
            {/* Asegúrate de que 'categories' es un array de strings */}
            {categories.map(category => (
              <SelectItem key={category} value={category}>{category}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 🔑 Unidad (unidad_medida) */}
      <div className="space-y-2">
        <Label htmlFor="unit">Unidad *</Label>
        <Select 
          // FIX: Usar unit y prevenir advertencia de React
          value={formData.unit || ""} 
          onValueChange={(value) => setFormData({ ...formData, unit: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Unidad" /> 
          </SelectTrigger>
          <SelectContent>
            {/* Estos deben coincidir EXACTAMENTE con tu UnidadMedidaEnum de Python */}
            <SelectItem value="KG">Kilogramos</SelectItem>
            <SelectItem value="G">Gramos</SelectItem>
            <SelectItem value="L">Litros</SelectItem>
            <SelectItem value="ML">Mililitros</SelectItem>
            <SelectItem value="UNIDAD">Unidades</SelectItem>
            <SelectItem value="CAJA">Caja</SelectItem>
            <SelectItem value="PAQUETE">Paquete</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Stock Mínimo (stock_minimo) */}
      <div className="space-y-2">
        <Label htmlFor="minStock">Stock Mínimo</Label>
        <Input
          id="minStock"
          type="number"
          step="0.01"
          placeholder="10"
          // FIX: Convertir a string vacío si es null/undefined para React
          value={formData.minStock === null || formData.minStock === undefined ? "" : formData.minStock} 
          // Guardar el valor tal como está en el input. El parseo ocurre en handleSubmit.
          onChange={(e) => setFormData(prev => ({ ...prev, minStock: e.target.value }))}
        />
      </div>
    </div>
    
    <div className="flex items-center space-x-4">
      {/* Perecible (perecible) */}
      <div className="flex items-center space-x-2 pt-2">
        <Input 
          id="isPerishable" 
          type="checkbox" 
          checked={formData.isPerishable || false} 
          onChange={(e) => setFormData(prev => ({ ...prev, isPerishable: e.target.checked }))} 
          className="w-4 h-4"
        />
        <Label htmlFor="isPerishable">Es Perecible</Label>
      </div>
    </div>

    {/* Notas Adicionales (descripcion) */}
    <div className="space-y-2">
      <Label htmlFor="notes">Notas Adicionales</Label>
      <Textarea
        id="notes"
        placeholder="Notas opcionales sobre el insumo..."
        value={formData.notes || ""} // FIX: Prevenir advertencia de React
        onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
      />
    </div>

    <div className="flex justify-end space-x-2 pt-4">
      <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
        Cancelar
      </Button>
      <Button 
          type="submit"
          // FIX: Deshabilitar si faltan campos obligatorios, forzando la selección de unidad
          disabled={!isFormValid} 
      >
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
            {/* 🛑 CABECERA: Usar 'Código' */}
            <TableHead>Código</TableHead>
            
            <TableHead>Insumo</TableHead>
            <TableHead>Categoría</TableHead>
            <TableHead>Stock</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Perecible</TableHead>           
            
            <TableHead>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredIngredients.map((ingredient) => {
            const status = getStockStatus(ingredient); // Se mantiene la lógica de estado (por stock
            
            return (
              <TableRow key={ingredient.id}>
                
                <TableCell className="font-medium">{ingredient.code}</TableCell>
                
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
                  {/* 🛑 COMPROBACIÓN DIRECTA DEL VALOR BOOLEANO */}
                  {ingredient.isPerishable ? (
                      // Si es TRUE (perecible)
                      <Badge variant="destructive">Sí</Badge> 
                  ) : (
                      // Si es FALSE (no perecible)
                      <Badge variant="secondary">No</Badge>
                  )}
               </TableCell>
                
                {/* 🛑 ELIMINADAS: Celdas de Vencimiento, Costo y Proveedor */}
                
                <TableCell>
                  {canEditInsumos && (
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
                  )}
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