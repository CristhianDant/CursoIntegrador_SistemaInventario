import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Plus, Search, Edit, Trash2, Package, TrendingUp, Calendar, DollarSign, Percent, Gift, AlertTriangle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Textarea } from "./ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { API_BASE_URL } from "../constants";
import { useAuth } from "../context/AuthContext";

// Interfaces
interface Recipe {
  id_receta: number;
  nombre_receta: string;
  costo_estimado: number;
}

interface ProductMovement {
  id: number;
  type: 'produccion' | 'venta' | 'merma';
  quantity: number;
  date: string;
  notes?: string;
  batchNumber?: string;
}

interface PromotionSuggestion {
  id: number;
  productId: number;
  type: 'discount' | 'combo' | 'clearance';
  title: string;
  description: string;
  suggestedDiscount?: number;
  comboProducts?: number[];
  daysUntilExpiry: number;
  potentialSavings: number;
  isActive: boolean;
}

interface FinishedProduct {
    id_producto: number; // FIX: Era 'id', debe ser 'id_producto'
    codigo_producto: string;
    nombre: string;
    descripcion: string;
    unidad_medida: string;
    stock_actual: number; // FIX: Era 'currentStock', debe ser 'stock_actual'
    stock_minimo: number; // FIX: Era 'minStock', debe ser 'stock_minimo'
    precio_venta: number;
    vida_util_dias: number | null;
    fecha_registro: string;
    anulado: boolean;

    // Campos de relleno/temporales de la UI (Mantenidos para evitar errores en otras partes)
    recipeId: number;
    recipeName: string;
    category: string;
    unitCost: number;
    profitMargin: number;
    expiryDate: string;
    productionDate: string;
    maxStock: number;
    status: 'Disponible' | 'Agotado' | 'Por Vencer';
    movements: ProductMovement[];
}

interface FormData {
    // ID del producto (para edición)
    id?: number; 
    
    // Campos que se envían a la API
    codigo_producto?: string;
    name: string;
    description: string;
    unitOfMeasure: string;
    minStock: number;
    sellingPrice: number;
    vida_util_dias: number | null;
    
    // Campos auxiliares del formulario
    recipeId?: number | null;
    anulado?: boolean;
}

// Mock data de recetas disponibles (fallback si la API falla)
const availableRecipes = [
  { id_receta: 1, nombre_receta: "Pastel de Chocolate Clásico", costo_estimado: 0.71 },
  { id_receta: 2, nombre_receta: "Galletas de Mantequilla", costo_estimado: 0.08 },
  { id_receta: 3, nombre_receta: "Pan Integral", costo_estimado: 0.35 },
  { id_receta: 4, nombre_receta: "Cheesecake de Fresa", costo_estimado: 1.25 },
];


 
// Sistema de promociones automáticas
const generatePromotionSuggestions = (products: FinishedProduct[]): PromotionSuggestion[] => {
  const suggestions: PromotionSuggestion[] = [];
  const today = new Date();
  
  products.forEach(product => {
    const expiryDate = new Date(product.expiryDate);
    const daysUntilExpiry = Math.ceil((expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiry <= 3 && product.stock_actual > 0) {
      // Sugerencia de descuento directo
      const suggestedDiscount = daysUntilExpiry <= 1 ? 40 : daysUntilExpiry <= 2 ? 25 : 15;
      suggestions.push({
        id: suggestions.length + 1,
        productId: product.id_producto,
        type: 'discount',
        title: `Descuento ${suggestedDiscount}% - ${product.nombre}`,
        description: `Aplicar ${suggestedDiscount}% de descuento por vencimiento en ${daysUntilExpiry} día(s)`,
        suggestedDiscount,
        daysUntilExpiry,
        potentialSavings: product.stock_actual * product.unitCost * (suggestedDiscount / 100),
        isActive: false
      });
      
      // Sugerencia de combo con productos complementarios
      const complementaryProducts = products.filter(p => 
        p.id_producto !== product.id_producto && 
        p.stock_actual > 0 && 
        (p.category === product.category || isComplementaryCategory(p.category, product.category))
      );
      
      if (complementaryProducts.length > 0) {
        const comboProduct = complementaryProducts[0];
        suggestions.push({
          id: suggestions.length + 1,
          productId: product.id_producto,
          type: 'combo',
          title: `Combo Especial: ${product.nombre} + ${comboProduct.nombre}`,
          description: `Combo de ${product.nombre} (por vencer) con ${comboProduct.nombre} - Precio especial`,
          comboProducts: [product.id_producto, comboProduct.id_producto],
          daysUntilExpiry,
          potentialSavings: product.stock_actual * product.unitCost * 0.3, // 30% de las pérdidas
          isActive: false
        });
      }
      
      // Sugerencia de liquidación urgente
      if (daysUntilExpiry <= 1) {
        suggestions.push({
          id: suggestions.length + 1,
          productId: product.id_producto,
          type: 'clearance',
          title: `¡LIQUIDACIÓN URGENTE! - ${product.nombre}`,
          description: `Venta de liquidación - Vence mañana. Precio especial para evitar merma total`,
          suggestedDiscount: 50,
          daysUntilExpiry,
          potentialSavings: product.stock_actual * product.unitCost * 0.5,
          isActive: false
        });
      }
    }
  });
  
  return suggestions;
};

const isComplementaryCategory = (category1: string, category2: string): boolean => {
  const complementaryPairs = [
    ['Pasteles', 'Postres'],
    ['Galletas', 'Postres'],
    ['Panes', 'Postres'],
    ['Decoraciones', 'Pasteles'],
    ['Decoraciones', 'Postres']
  ];
  
  return complementaryPairs.some(pair => 
    (pair[0] === category1 && pair[1] === category2) ||
    (pair[0] === category2 && pair[1] === category1)
  );
};

export function ProductManager() {
  const { canWrite } = useAuth();
  const canEditProducts = canWrite('PRODUCTOS');
  
  const [products, setProducts] = useState<FinishedProduct[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>(availableRecipes); // Estado para recetas cargadas de la API
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false);
  const [isPromotionDialogOpen, setIsPromotionDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<FinishedProduct | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<FinishedProduct | null>(null);
  const [formData, setFormData] = useState<Partial<FormData>>({});
  const [movementData, setMovementData] = useState<Partial<ProductMovement>>({});
  const [promotionSuggestions, setPromotionSuggestions] = useState<PromotionSuggestion[]>([]);
  const [selectedPromotion, setSelectedPromotion] = useState<PromotionSuggestion | null>(null);

 const fetchProducts = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/productos_terminados/`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error('Error al cargar productos desde el servidor.');
        }

        const data = await response.json();
        
        // Verifica que la respuesta tenga el formato { success: true, data: [...] }
        if (data.success && Array.isArray(data.data)) {
            
            // ESTE ES EL MAPEO CRÍTICO DE NOMBRES
            const loadedProducts: FinishedProduct[] = data.data.map((p: any) => ({
                // Mapeo de DB (snake_case) a React (snake_case)
                id_producto: p.id_producto,               
                codigo_producto: p.codigo_producto, // Nuevo campo
                nombre: p.nombre,                   
                descripcion: p.descripcion || "",
                unidad_medida: p.unidad_medida, // ¡CRÍTICO! Usar el campo real de la DB
                stock_actual: parseFloat(p.stock_actual || 0),
                stock_minimo: parseFloat(p.stock_minimo || 0),   
                precio_venta: parseFloat(p.precio_venta || 0),
                vida_util_dias: p.vida_util_dias,
                fecha_registro: p.fecha_registro,
                anulado: p.anulado,

                // Valores de relleno necesarios para que la interfaz NO falle
                recipeName: p.nombre_receta || "N/A",  
                category: p.categoria || "Sin Categoría",
                unitCost: parseFloat(p.costo_unitario || 0),
                profitMargin: 0.00, // Calcular con datos reales
                expiryDate: p.fecha_vencimiento || new Date().toISOString().split('T')[0],
                productionDate: new Date(p.fecha_registro).toISOString().split('T')[0], // Usar fecha_registro
                maxStock: 20, // Valor hardcodeado temporal
                recipeId: 0, // Valor hardcodeado temporal
                status: 'Disponible', // Debe ser calculado con stock_actual y stock_minimo
                movements: [],
            })) as FinishedProduct[];
            
            setProducts(loadedProducts);
        }

    } catch (error) {
        console.error("Fallo la carga de productos. El error es:", error);
    }
};

// Función para cargar recetas desde la API
const fetchRecipes = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/recetas/listar/simple`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            console.warn('Error al cargar recetas desde el servidor, usando datos por defecto.');
            return; // Usa los mock data como fallback
        }

        const data = await response.json();
        
        // Verifica que la respuesta tenga el formato { success: true, data: [...] }
        if (data.success && Array.isArray(data.data)) {
            const loadedRecipes: Recipe[] = data.data.map((r: any) => ({
                id_receta: r.id_receta,
                nombre_receta: r.nombre_receta,
                costo_estimado: parseFloat(r.costo_estimado || 0),
            }));
            
            setRecipes(loadedRecipes);
        }

    } catch (error) {
        console.error("Fallo la carga de recetas. Usando datos por defecto:", error);
        // Si hay error, mantiene los mock data
    }
};

useEffect(() => {
        // Llama a la función que realiza la petición a la API
        fetchProducts(); 
        fetchRecipes(); // Cargar recetas al montar el componente
    }, []); // El array vacío '[]' es crucial para que se ejecute solo al inicio.

  // Generar sugerencias de promociones automáticamente
  useEffect(() => {
    setPromotionSuggestions(generatePromotionSuggestions(products));
  }, [products]);

  // Función para calcular el estado de un producto
  const getProductStatus = (product: FinishedProduct) => {
    if (product.stock_actual <= 0) return 'Agotado';
    if (product.stock_actual <= product.stock_minimo) return 'Stock Bajo';
    return 'Disponible';
  };

  const filteredProducts = products.filter(product => {
    const productName = product.nombre || '';
    const productCode = product.codigo_producto || '';
    const matchesSearch = productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         productCode.toLowerCase().includes(searchTerm.toLowerCase());
    const productStatus = getProductStatus(product);
    const matchesStatus = selectedStatus === "all" || productStatus === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const generateBatchNumber = (recipeId: number) => {
    const today = new Date();
    const dateStr = today.toISOString().slice(2, 10).replace(/-/g, '');
    const recipe = recipes.find(r => r.id_receta === recipeId);
    const prefix = recipe?.nombre_receta.substring(0, 2).toUpperCase() || 'PR';
    const sequence = '001'; // En una implementación real, esto sería incremental
    return `${prefix}${dateStr}${sequence}`;
  };

 const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Variables de control
    const idToUpdate = editingProduct?.id_producto; 
    
    if (editingProduct && idToUpdate) { // Lógica de Edición (PUT)
        
        // Mapeo: formData (UI/camelCase) -> updatedData (API/snake_case)
        const updatedData = {
            // codigo_producto es requerido por el schema
            codigo_producto: editingProduct.codigo_producto,
            // Usamos '!' para indicar que estos campos deben existir al enviar el formulario.
            nombre: formData.name!, 
            descripcion: formData.description || "",
            unidad_medida: formData.unitOfMeasure || editingProduct.unidad_medida, 
            stock_minimo: formData.minStock!,
            // Usamos '?? null' para enviar None a Python si el campo está vacío.
            vida_util_dias: formData.vida_util_dias ?? null, 
            precio_venta: formData.sellingPrice!,
            anulado: formData.anulado ?? false, 
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/v1/productos_terminados/${idToUpdate}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData), 
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al actualizar el producto.');
            }

            await response.json(); 
            await fetchProducts(); 
            toast.success("Producto actualizado correctamente");

        } catch (error) {
            console.error("Fallo la actualización del producto. El error es:", error);
            toast.error("Error al actualizar el producto");
        }
        
    } else { // Lógica de Creación (POST)
        
        // Mapeo: formData (UI/camelCase) -> newProductData (API/snake_case)
        const newProductData = {
            // Usamos el código del form, o generamos uno si es nulo.
            codigo_producto: formData.codigo_producto || generateBatchNumber(formData.recipeId || 0),
            // Usamos '!' para indicar que estos campos deben existir al enviar el formulario.
            nombre: formData.name!, 
            descripcion: formData.description || "",
            unidad_medida: formData.unitOfMeasure || "UNIDAD", 
            stock_minimo: formData.minStock!,
            vida_util_dias: formData.vida_util_dias ?? 30, 
            precio_venta: formData.sellingPrice!,
            // stock_actual y fecha_registro no se envían.
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/v1/productos_terminados/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newProductData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al crear el producto.');
            }

            await response.json();
            fetchProducts(); 

        } catch (error) {
            console.error("Fallo la creación del producto. El error es:", error);
        }
    }
    
    // Limpieza y cierre
    setIsDialogOpen(false);
    setEditingProduct(null);
    setFormData({}); 
};

// --- Funciones Auxiliares (sin cambios, asumiendo que los setters existen) ---

const openProductionDialog = (product: FinishedProduct) => {
    // Asumo que setSelectedProduct, setMovementData e setIsMovementDialogOpen están definidos
    setSelectedProduct(product);
    setMovementData({ type: 'produccion', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
};

const openSaleDialog = (product: FinishedProduct) => {
    // Asumo que setSelectedProduct, setMovementData e setIsMovementDialogOpen están definidos
    setSelectedProduct(product);
    setMovementData({ type: 'venta', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
};

const handleMovementSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProduct || !movementData.quantity || !movementData.date) {
        toast.error("Datos incompletos para el movimiento");
        return;
    }

    // Generar número de movimiento único
    const generateMovementNumber = () => {
        const now = new Date();
        const prefix = movementData.type === 'produccion' ? 'PROD' : movementData.type === 'venta' ? 'VTA' : 'MRM';
        return `${prefix}-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
    };

    // Mapear tipo de movimiento del frontend al backend
    const tipoMovimientoMap: { [key: string]: string } = {
        'produccion': 'ENTRADA',
        'venta': 'SALIDA',
        'merma': 'SALIDA'
    };

    const movimientoData = {
        numero_movimiento: generateMovementNumber(),
        id_producto: selectedProduct.id_producto,
        tipo_movimiento: tipoMovimientoMap[movementData.type || 'produccion'],
        motivo: movementData.type === 'produccion' ? 'Producción' : movementData.type === 'venta' ? 'Venta' : 'Merma',
        cantidad: movementData.quantity,
        precio_venta: movementData.type === 'venta' ? selectedProduct.precio_venta : 0,
        id_user: 1, // TODO: Obtener del usuario logueado
        observaciones: movementData.notes || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/v1/movimientos_productos_terminados/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(movimientoData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.data || 'Error al registrar el movimiento');
        }

        await response.json();
        await fetchProducts(); // Recargar productos para ver el stock actualizado
        toast.success(`${movementData.type === 'produccion' ? 'Producción' : 'Venta'} registrada correctamente`);
        
    } catch (error: any) {
        console.error("Fallo el registro del movimiento:", error);
        toast.error(error.message || "Error al registrar el movimiento");
    }
    
    setIsMovementDialogOpen(false);
    setMovementData({});
    setSelectedProduct(null);
};

const handleEdit = (product: FinishedProduct) => {
  setEditingProduct(product);
  
  // *** Mapeo CRÍTICO: Backend (snake_case) a UI (camelCase/form) ***
  setFormData({
    // Propiedades API/DB (product.)     = Propiedades Formulario (setFormData)
    name: product.nombre, // FIX: Usa product.nombre
    description: product.descripcion,
    minStock: product.stock_minimo,
    sellingPrice: product.precio_venta,
    unitOfMeasure: product.unidad_medida,
    vida_util_dias: product.vida_util_dias, 
    anulado: product.anulado, 
    codigo_producto: product.codigo_producto,
    recipeId: product.recipeId, 
  });
  setIsDialogOpen(true);
};

  const handleDelete = (id: number) => {
    setProducts(prev => prev.filter(product => product.id_producto !== id));
  };

  const openAddDialog = () => {
    setEditingProduct(null);
    setFormData({
      minStock: 5,
      unitOfMeasure: 'UNIDAD',
      vida_util_dias: 30
    });
    setIsDialogOpen(true);
  };

  const activatePromotion = (promotion: PromotionSuggestion) => {
    setPromotionSuggestions(prev =>
      prev.map(p => p.id === promotion.id ? { ...p, isActive: true } : p)
    );
    
    // Aquí se podría integrar con un sistema de promociones real
    console.log(`Promoción activada: ${promotion.title}`);
  };

  const openPromotionDialog = () => {
    setPromotionSuggestions(generatePromotionSuggestions(products));
    setIsPromotionDialogOpen(true);
  };

  const getPromotionTypeIcon = (type: string) => {
    switch (type) {
      case 'discount': return <Percent className="h-4 w-4" />;
      case 'combo': return <Gift className="h-4 w-4" />;
      case 'clearance': return <AlertTriangle className="h-4 w-4" />;
      default: return <Percent className="h-4 w-4" />;
    }
  };

  const getPromotionTypeColor = (type: string) => {
    switch (type) {
      case 'discount': return 'bg-blue-100 text-blue-800';
      case 'combo': return 'bg-purple-100 text-purple-800';
      case 'clearance': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Estadísticas basadas en datos reales
  const stats = {
    total: products.length,
    available: products.filter(p => p.stock_actual > p.stock_minimo).length,
    outOfStock: products.filter(p => p.stock_actual <= 0).length,
    lowStock: products.filter(p => p.stock_actual > 0 && p.stock_actual <= p.stock_minimo).length,
    totalValue: products.reduce((sum, p) => sum + (p.stock_actual * p.precio_venta), 0),
    activeSuggestions: promotionSuggestions.filter(s => !s.isActive).length,
    potentialSavings: promotionSuggestions.reduce((sum, s) => sum + s.potentialSavings, 0)
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Productos Terminados</h2>
          <p className="text-muted-foreground">Gestiona los productos elaborados con tus recetas</p>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={openPromotionDialog} variant="outline" className="relative">
            <Gift className="h-4 w-4 mr-2" />
            Promociones
            {stats.activeSuggestions > 0 && (
              <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {stats.activeSuggestions}
              </Badge>
            )}
          </Button>
          {canEditProducts && (
            <Button onClick={openAddDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Producto
            </Button>
          )}
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-2 md:grid-cols-7 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Productos</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Package className="h-5 w-5 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Disponibles</p>
                <p className="text-2xl font-bold text-green-600">{stats.available}</p>
              </div>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Agotados</p>
                <p className="text-2xl font-bold text-red-600">{stats.outOfStock}</p>
              </div>
              <Package className="h-5 w-5 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Stock Bajo</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.lowStock}</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Promociones</p>
                <p className="text-2xl font-bold text-orange-600">{stats.activeSuggestions}</p>
              </div>
              <Gift className="h-5 w-5 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Valor Total</p>
                <p className="text-2xl font-bold">${stats.totalValue.toFixed(0)}</p>
              </div>
              <DollarSign className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar productos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="Disponible">Disponible</SelectItem>
                <SelectItem value="Stock Bajo">Stock Bajo</SelectItem>
                <SelectItem value="Agotado">Agotado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de productos */}
      <Card>
        <CardHeader>
          <CardTitle>Inventario de Productos</CardTitle>
          <CardDescription>
            {filteredProducts.length} productos encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Producto</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Precio Venta</TableHead>
                  <TableHead>Vida Útil</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product) => {
                  // Calcular estado dinámicamente
                  const getProductStatus = () => {
                    if (product.stock_actual <= 0) return 'Agotado';
                    if (product.stock_actual <= product.stock_minimo) return 'Stock Bajo';
                    return 'Disponible';
                  };
                  const status = getProductStatus();
                  const statusColor = status === 'Disponible' ? 'bg-green-100 text-green-800' 
                    : status === 'Agotado' ? 'bg-red-100 text-red-800' 
                    : 'bg-yellow-100 text-yellow-800';
                  
                  return (
                  <TableRow key={product.id_producto}>
                    <TableCell>
                      <span className="font-mono text-sm">{product.codigo_producto}</span>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.nombre}</div>
                        <div className="text-sm text-muted-foreground">{product.descripcion?.substring(0, 40)}{product.descripcion?.length > 40 ? '...' : ''}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.stock_actual} {product.unidad_medida?.toLowerCase()}</div>
                        <div className="text-xs text-muted-foreground">
                          Mínimo: {product.stock_minimo}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColor}>
                        {status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium text-green-600">S/ {product.precio_venta.toFixed(2)}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{product.vida_util_dias ? `${product.vida_util_dias} días` : '-'}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openProductionDialog(product)}
                          title="Registrar Producción"
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openSaleDialog(product)}
                          title="Registrar Venta"
                          disabled={product.stock_actual <= 0} 
                        >
                          <DollarSign className="h-3 w-3" />
                        </Button>
                        {canEditProducts && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(product)}
                            title="Editar"
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                        )}
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

      {/* Dialog para nuevo/editar producto (Mantiene camelCase en formData, lo cual es correcto) */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingProduct ? "Editar Producto" : "Nuevo Producto"}
            </DialogTitle>
            <DialogDescription>
              {editingProduct ? "Modifica la información del producto" : "Crea un nuevo producto basado en una receta"}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="productName">Nombre del Producto</Label>
                <Input
                  id="productName"
                  name="productName"
                  autoComplete="off"
                  placeholder="Ej: Pastel de Chocolate Premium"
                  value={formData.name || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="recipeId">Receta Base (opcional)</Label>
                <Select 
                  value={formData.recipeId?.toString() || "none"} 
                  onValueChange={(value: string) => {
                    const recipeId = value === "none" ? null : parseInt(value);
                    setFormData(prev => ({ 
                      ...prev, 
                      recipeId
                    }));
                  }}
                  name="recipeId"
                >
                  <SelectTrigger id="recipeId">
                    <SelectValue placeholder="Selecciona receta" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Sin receta</SelectItem>
                    {recipes.map(recipe => (
                      <SelectItem key={recipe.id_receta} value={recipe.id_receta.toString()}>
                        {recipe.nombre_receta} (S/ {recipe.costo_estimado.toFixed(2)})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="productDescription">Descripción</Label>
              <Textarea
                id="productDescription"
                name="productDescription"
                autoComplete="off"
                placeholder="Descripción del producto..."
                value={formData.description || ""}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="unitOfMeasure">Unidad de Medida</Label>
                <Select 
                  value={formData.unitOfMeasure || "UNIDAD"} 
                  onValueChange={(value: string) => setFormData(prev => ({ ...prev, unitOfMeasure: value }))}
                  name="unitOfMeasure"
                >
                  <SelectTrigger id="unitOfMeasure">
                    <SelectValue placeholder="Selecciona unidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="UNIDAD">Unidad</SelectItem>
                    <SelectItem value="KILOGRAMO">Kilogramo</SelectItem>
                    <SelectItem value="GRAMO">Gramo</SelectItem>
                    <SelectItem value="LITRO">Litro</SelectItem>
                    <SelectItem value="MILILITRO">Mililitro</SelectItem>
                    <SelectItem value="DOCENA">Docena</SelectItem>
                    <SelectItem value="CAJA">Caja</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="minStock">Stock Mínimo</Label>
                <Input
                  id="minStock"
                  name="minStock"
                  autoComplete="off"
                  type="number"
                  value={formData.minStock || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, minStock: parseInt(e.target.value) }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="vida_util_dias">Vida Útil (días)</Label>
                <Input
                  id="vida_util_dias"
                  name="vida_util_dias"
                  autoComplete="off"
                  type="number"
                  placeholder="Ej: 30"
                  value={formData.vida_util_dias || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, vida_util_dias: parseInt(e.target.value) || null }))}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="sellingPrice">Precio de Venta (S/)</Label>
                <Input
                  id="sellingPrice"
                  name="sellingPrice"
                  autoComplete="off"
                  type="number"
                  step="0.01"
                  value={formData.sellingPrice || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, sellingPrice: parseFloat(e.target.value) }))}
                  required
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingProduct ? "Actualizar" : "Crear Producto"}
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
              {movementData.type === 'produccion' ? 'Registrar Producción' : 'Registrar Venta'}
            </DialogTitle>
            <DialogDescription>
              {selectedProduct?.nombre} - Lote: {selectedProduct?.codigo_producto} {/* CORRECCIÓN: name -> nombre, batchNumber -> codigo_producto */}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleMovementSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantity">Cantidad</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  max={movementData.type === 'venta' ? selectedProduct?.stock_actual : undefined} 
                  value={movementData.quantity || ""}
                  onChange={(e) => setMovementData(prev => ({ ...prev, quantity: parseInt(e.target.value) }))}
                  required
                />
                {movementData.type === 'venta' && (
                  <p className="text-xs text-muted-foreground">
                    Stock disponible: {selectedProduct?.stock_actual} {/* CORRECCIÓN: currentStock -> stock_actual */}
                  </p>
                )}
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

            <div className="space-y-2">
              <Label htmlFor="notes">Notas (opcional)</Label>
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
                Registrar {movementData.type === 'produccion' ? 'Producción' : 'Venta'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Dialog para Sistema de Promociones */}
      <Dialog open={isPromotionDialogOpen} onOpenChange={setIsPromotionDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Gift className="h-5 w-5 mr-2" />
              Sistema de Promociones Automáticas
            </DialogTitle>
            <DialogDescription>
              Sugerencias automáticas para evitar mermas de productos por vencer
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Resumen de ahorros potenciales */}
            <Card className="bg-green-50">
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-green-800">Ahorros Potenciales</h4>
                    <p className="text-2xl font-bold text-green-600">
                      ${stats.potentialSavings.toFixed(2)}
                    </p>
                    <p className="text-sm text-green-700">
                      Al activar todas las promociones sugeridas
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            {/* Lista de sugerencias */}
            <div className="space-y-4">
              <h4 className="font-medium">Promociones Sugeridas ({promotionSuggestions.filter(s => !s.isActive).length})</h4>
              
              {promotionSuggestions.filter(s => !s.isActive).length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <Gift className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground">No hay promociones sugeridas en este momento</p>
                    <p className="text-sm text-muted-foreground">
                      Las sugerencias aparecerán automáticamente cuando productos estén por vencer
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {promotionSuggestions.filter(s => !s.isActive).map((suggestion) => {
                    const product = products.find(p => p.id_producto === suggestion.productId); // CORRECCIÓN: p.id -> p.id_producto
                    return (
                      <Card key={suggestion.id} className="border-l-4 border-l-orange-400">
                        <CardHeader className="pb-2">
                          <div className="flex justify-between items-start">
                            <div className="flex items-center space-x-2">
                              {getPromotionTypeIcon(suggestion.type)}
                              <Badge className={getPromotionTypeColor(suggestion.type)}>
                                {suggestion.type === 'discount' && 'Descuento'}
                                {suggestion.type === 'combo' && 'Combo'}
                                {suggestion.type === 'clearance' && 'Liquidación'}
                              </Badge>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded ${
                              suggestion.daysUntilExpiry <= 1 ? 'bg-red-100 text-red-800' :
                              suggestion.daysUntilExpiry <= 2 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {suggestion.daysUntilExpiry} día(s)
                            </span>
                          </div>
                          <CardTitle className="text-base">{suggestion.title}</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <p className="text-sm text-muted-foreground">
                            {suggestion.description}
                          </p>
                          
                          <div className="flex justify-between text-sm">
                            <span>Producto:</span>
                            <span className="font-medium">{product?.nombre}</span> {/* CORRECCIÓN: product?.name -> product?.nombre */}
                          </div>
                          
                          <div className="flex justify-between text-sm">
                            <span>Stock actual:</span>
                            <span className="font-medium">{product?.stock_actual} unidades</span> {/* CORRECCIÓN: product?.currentStock -> product?.stock_actual */}
                          </div>
                          
                          {suggestion.suggestedDiscount && (
                            <div className="flex justify-between text-sm">
                              <span>Descuento sugerido:</span>
                              <span className="font-medium text-green-600">
                                {suggestion.suggestedDiscount}%
                              </span>
                            </div>
                          )}
                          
                          <div className="flex justify-between text-sm">
                            <span>Ahorro potencial:</span>
                            <span className="font-medium text-green-600">
                              ${suggestion.potentialSavings.toFixed(2)}
                            </span>
                          </div>
                          
                          {suggestion.type === 'combo' && suggestion.comboProducts && (
                            <div className="text-sm">
                              <span>Productos en combo:</span>
                              <div className="mt-1">
                                {suggestion.comboProducts.map(productId => {
                                  const comboProduct = products.find(p => p.id_producto === productId); // CORRECCIÓN: p.id -> p.id_producto
                                  return (
                                    <Badge key={productId} variant="outline" className="mr-1 text-xs">
                                      {comboProduct?.nombre} {/* CORRECCIÓN: comboProduct?.name -> comboProduct?.nombre */}
                                    </Badge>
                                  );
                                })}
                              </div>
                            </div>
                          )}

                          <div className="flex space-x-2 pt-2">
                            <Button
                              size="sm"
                              onClick={() => activatePromotion(suggestion)}
                              className="flex-1"
                            >
                              Activar Promoción
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setPromotionSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
                              }}
                            >
                              Descartar
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Promociones activas */}
            {promotionSuggestions.filter(s => s.isActive).length > 0 && (
              <div className="space-y-4">
                <h4 className="font-medium text-green-600">
                  Promociones Activas ({promotionSuggestions.filter(s => s.isActive).length})
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {promotionSuggestions.filter(s => s.isActive).map((suggestion) => {
                    // Nota: Aquí se mantiene el mapeo, aunque no se usa product en el cuerpo, es buena práctica
                    const product = products.find(p => p.id_producto === suggestion.productId); // CORRECCIÓN: p.id -> p.id_producto
                    return (
                      <Card key={suggestion.id} className="border-l-4 border-l-green-400 bg-green-50">
                        <CardHeader className="pb-2">
                          <div className="flex justify-between items-start">
                            <div className="flex items-center space-x-2">
                              {getPromotionTypeIcon(suggestion.type)}
                              <Badge className="bg-green-100 text-green-800">
                                Activa
                              </Badge>
                            </div>
                            <span className="text-xs text-green-600 font-medium">
                              ✓ Aplicada
                            </span>
                          </div>
                          <CardTitle className="text-base text-green-800">{suggestion.title}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-green-700">
                            {suggestion.description}
                          </p>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
          
          <div className="flex justify-end pt-4">
            <Button onClick={() => setIsPromotionDialogOpen(false)}>
              Cerrar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}