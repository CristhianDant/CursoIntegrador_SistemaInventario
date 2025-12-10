import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Plus, Search, Edit, Trash2, Package, TrendingUp, Calendar, DollarSign, Percent, Gift, AlertTriangle, ChefHat, Loader2, CheckCircle, XCircle, FileWarning, TrendingDown } from "lucide-react";
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
import { TablePagination, usePagination } from "./ui/table-pagination";

// Interfaces
interface Recipe {
  id_receta: number;
  nombre_receta: string;
  costo_estimado: number;
}

// Interfaces para el sistema de producción
interface RecetaCompleta {
  id_receta: number;
  codigo_receta: string;
  nombre_receta: string;
  descripcion: string;
  rendimiento_producto_terminado: number;
  costo_estimado: number;
  detalles: RecetaDetalle[];
}

interface RecetaDetalle {
  id_receta_detalle: number;
  id_insumo: number;
  cantidad: number;
  costo_unitario: number;
  costo_total: number;
  es_opcional: boolean;
  observaciones: string | null;
}

interface InsumoRequerido {
  id_insumo: number;
  codigo_insumo: string;
  nombre_insumo: string;
  unidad_medida: string;
  cantidad_requerida: number;
  stock_disponible: number;
  es_suficiente: boolean;
}

interface ValidacionStock {
  id_receta: number;
  nombre_receta: string;
  cantidad_batch: number;
  puede_producir: boolean;
  insumos: InsumoRequerido[];
  mensaje: string;
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

// Interface para Insumos (para mermas)
interface Insumo {
    id_insumo: number;
    codigo: string;
    nombre: string;
    categoria: string;
    stock_actual: number;
    stock_minimo: number;
    unidad_medida: string;
    precio_promedio: number;
}

// Interface para Mermas
interface Merma {
    id_merma: number;
    numero_registro: string;
    tipo: 'VENCIMIENTO' | 'HONGEADO' | 'DAÑO' | 'PRODUCCION';
    causa: string;
    cantidad: number;
    costo_unitario: number;
    costo_total: number;
    fecha_caso: string;
    id_insumo: number | null;
    id_producto: number | null;
    id_lote: number | null;
    id_user_responsable: number;
    observacion: string | null;
    estado: string;
    anulado: boolean;
    // Campos para mostrar nombres (se agregan en frontend)
    nombre_producto?: string;
    nombre_insumo?: string;
}

interface MermaFormData {
    tipo: string;
    tipoItem: 'producto' | 'insumo';
    causa: string;
    cantidad: number;
    costo_unitario: number;
    costo_total: number;
    fecha_caso: string;
    id_producto: number | null;
    id_insumo: number | null;
    id_user_responsable: number;
    observacion: string;
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

// Función para formatear números de forma amigable (sin decimales innecesarios)
const formatNumber = (value: number | string | null | undefined): string => {
  // Convertir a número si es string
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  // Validar que sea un número válido
  if (num === null || num === undefined || isNaN(Number(num))) return '0';
  
  // Si es entero, mostrar sin decimales
  if (Number.isInteger(num)) return num.toString();
  
  // Si tiene decimales, mostrar máximo 2 y eliminar ceros finales
  const formatted = Number(num).toFixed(2);
  return parseFloat(formatted).toString();
};

export function ProductManager() {
  const { canWrite } = useAuth();
  const canEditProducts = canWrite('PRODUCTOS');
  
  const [products, setProducts] = useState<FinishedProduct[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]); // Recetas cargadas desde la API
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
  
  // Estados para el sistema de producción
  const [isProductionDialogOpen, setIsProductionDialogOpen] = useState(false);
  const [selectedRecipeId, setSelectedRecipeId] = useState<number | null>(null);
  const [selectedRecipeDetails, setSelectedRecipeDetails] = useState<RecetaCompleta | null>(null);
  const [cantidadBatch, setCantidadBatch] = useState<number>(1);
  const [validacionStock, setValidacionStock] = useState<ValidacionStock | null>(null);
  const [loadingValidation, setLoadingValidation] = useState(false);
  const [loadingProduction, setLoadingProduction] = useState(false);

  // Estados para el sistema de mermas
  const [activeTab, setActiveTab] = useState("productos");
  const [mermas, setMermas] = useState<Merma[]>([]);
  const [insumos, setInsumos] = useState<Insumo[]>([]);
  const [isMermaDialogOpen, setIsMermaDialogOpen] = useState(false);
  const [mermaFormData, setMermaFormData] = useState<MermaFormData>({
    tipo: 'PRODUCCION',
    tipoItem: 'insumo',
    causa: '',
    cantidad: 0,
    costo_unitario: 0,
    costo_total: 0,
    fecha_caso: new Date().toISOString().split('T')[0],
    id_producto: null,
    id_insumo: null,
    id_user_responsable: 1,
    observacion: ''
  });
  const [mermaSearchTerm, setMermaSearchTerm] = useState("");
  const [selectedMermaTipo, setSelectedMermaTipo] = useState("all");

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
            console.error('Error al cargar recetas desde el servidor.');
            toast.error('Error al cargar las recetas');
            return;
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
        console.error("Error al cargar recetas:", error);
        toast.error('Error de conexión al cargar recetas');
    }
};

// Función para cargar mermas desde la API
const fetchMermas = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/mermas/`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            console.error('Error al cargar mermas desde el servidor.');
            return;
        }

        const data = await response.json();
        
        if (data.success && Array.isArray(data.data)) {
            setMermas(data.data);
        }
    } catch (error) {
        console.error("Error al cargar mermas:", error);
    }
};

// Función para cargar insumos desde la API (para mermas)
const fetchInsumos = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/insumos/`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            console.error('Error al cargar insumos desde el servidor.');
            return;
        }

        const data = await response.json();
        
        if (data.success && Array.isArray(data.data)) {
            const loadedInsumos: Insumo[] = data.data.map((i: any) => ({
                id_insumo: i.id_insumo,
                codigo: i.codigo,
                nombre: i.nombre,
                categoria: i.categoria || 'Sin categoría',
                stock_actual: parseFloat(i.stock_actual || 0),
                stock_minimo: parseFloat(i.stock_minimo || 0),
                unidad_medida: i.unidad_medida,
                precio_promedio: parseFloat(i.precio_promedio || 0),
            }));
            setInsumos(loadedInsumos);
        }
    } catch (error) {
        console.error("Error al cargar insumos:", error);
    }
};

useEffect(() => {
        // Llama a la función que realiza la petición a la API
        fetchProducts(); 
        fetchRecipes(); // Cargar recetas al montar el componente
        fetchMermas(); // Cargar mermas al montar el componente
        fetchInsumos(); // Cargar insumos al montar el componente (para mermas)
    }, []); // El array vacío '[]' es crucial para que se ejecute solo al inicio.

  // Generar sugerencias de promociones automáticamente
  useEffect(() => {
    setPromotionSuggestions(generatePromotionSuggestions(products));
  }, [products]);

  // ============ FUNCIONES DE PRODUCCIÓN ============
  
  // Cargar detalles de una receta específica
  const fetchRecipeDetails = async (recetaId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/recetas/${recetaId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) throw new Error('Error al cargar detalles de la receta');
      
      const data = await response.json();
      if (data.success && data.data) {
        setSelectedRecipeDetails(data.data);
      }
    } catch (error) {
      console.error("Error cargando detalles de receta:", error);
      toast.error("Error al cargar los detalles de la receta");
    }
  };

  // Validar stock antes de producir
  const validarStockProduccion = async () => {
    if (!selectedRecipeId || cantidadBatch <= 0) {
      toast.error("Selecciona una receta y cantidad válida");
      return;
    }

    setLoadingValidation(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/v1/produccion/validar-stock?id_receta=${selectedRecipeId}&cantidad_batch=${cantidadBatch}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) throw new Error('Error al validar stock');

      const data = await response.json();
      if (data.success && data.data) {
        setValidacionStock(data.data);
        if (!data.data.puede_producir) {
          toast.warning("Stock insuficiente para algunos insumos");
        } else {
          toast.success("¡Stock validado! Puedes ejecutar la producción");
        }
      }
    } catch (error) {
      console.error("Error validando stock:", error);
      toast.error("Error al validar el stock disponible");
    } finally {
      setLoadingValidation(false);
    }
  };

  // Ejecutar producción
  const ejecutarProduccion = async () => {
    if (!selectedRecipeId || !validacionStock?.puede_producir) {
      toast.error("Debes validar el stock primero");
      return;
    }

    setLoadingProduction(true);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/produccion/ejecutar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_receta: selectedRecipeId,
          cantidad_batch: cantidadBatch,
          id_user: 1, // TODO: Obtener del usuario logueado
          observaciones: `Producción desde interfaz web`
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.data || 'Error al ejecutar producción');
      }

      const data = await response.json();
      if (data.success) {
        toast.success(`¡Producción exitosa! ${data.data.cantidad_producida} unidades producidas`);
        await fetchProducts(); // Actualizar lista de productos
        closeProductionDialog();
      }
    } catch (error: any) {
      console.error("Error ejecutando producción:", error);
      toast.error(error.message || "Error al ejecutar la producción");
    } finally {
      setLoadingProduction(false);
    }
  };

  // Abrir dialog de producción
  const openProductionDialogWithRecipe = () => {
    setSelectedRecipeId(null);
    setSelectedRecipeDetails(null);
    setCantidadBatch(1);
    setValidacionStock(null);
    setIsProductionDialogOpen(true);
  };

  // Cerrar dialog de producción
  const closeProductionDialog = () => {
    setIsProductionDialogOpen(false);
    setSelectedRecipeId(null);
    setSelectedRecipeDetails(null);
    setCantidadBatch(1);
    setValidacionStock(null);
  };

  // Manejar selección de receta
  const handleRecipeSelection = async (recetaId: string) => {
    const id = parseInt(recetaId);
    setSelectedRecipeId(id);
    setValidacionStock(null);
    await fetchRecipeDetails(id);
  };

  // ============ FIN FUNCIONES DE PRODUCCIÓN ============

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

  // Paginación
  const {
    currentPage,
    setCurrentPage,
    itemsPerPage,
    setItemsPerPage,
    totalPages,
    totalItems,
    paginatedItems: paginatedProducts,
  } = usePagination(filteredProducts, 10);

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

  // ============ FUNCIONES DE MERMAS ============
  
  const generateMermaNumber = () => {
    const now = new Date();
    return `MRM-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
  };

  const openMermaDialog = (product?: FinishedProduct, insumo?: Insumo) => {
    if (insumo) {
      setMermaFormData({
        tipo: 'PRODUCCION',
        tipoItem: 'insumo',
        causa: '',
        cantidad: 0,
        costo_unitario: insumo.precio_promedio || 0,
        costo_total: 0,
        fecha_caso: new Date().toISOString().split('T')[0],
        id_producto: null,
        id_insumo: insumo.id_insumo,
        id_user_responsable: 1,
        observacion: ''
      });
    } else {
      setMermaFormData({
        tipo: product ? 'VENCIMIENTO' : 'PRODUCCION',
        tipoItem: product ? 'producto' : 'insumo',
        causa: '',
        cantidad: 0,
        costo_unitario: product?.precio_venta || 0,
        costo_total: 0,
        fecha_caso: new Date().toISOString().split('T')[0],
        id_producto: product?.id_producto || null,
        id_insumo: null,
        id_user_responsable: 1,
        observacion: ''
      });
    }
    setIsMermaDialogOpen(true);
  };

  const handleMermaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const esInsumo = mermaFormData.tipoItem === 'insumo';
    
    if (esInsumo) {
      // Validación para insumos
      if (!mermaFormData.id_insumo || !mermaFormData.cantidad || mermaFormData.cantidad <= 0) {
        toast.error("Selecciona un insumo y cantidad válida");
        return;
      }

      const insumo = insumos.find(i => i.id_insumo === mermaFormData.id_insumo);
      if (!insumo) {
        toast.error("Insumo no encontrado");
        return;
      }

      if (mermaFormData.cantidad > insumo.stock_actual) {
        toast.error(`Stock insuficiente. Disponible: ${insumo.stock_actual}`);
        return;
      }

      const costoTotal = (mermaFormData.cantidad || 0) * (mermaFormData.costo_unitario || 0);

      const mermaData = {
        numero_registro: generateMermaNumber(),
        tipo: mermaFormData.tipo,
        causa: mermaFormData.causa || `Merma de insumo por ${mermaFormData.tipo?.toLowerCase()}`,
        cantidad: mermaFormData.cantidad,
        costo_unitario: mermaFormData.costo_unitario,
        costo_total: costoTotal,
        fecha_caso: new Date().toISOString(),
        id_insumo: mermaFormData.id_insumo,
        id_producto: null,
        id_lote: null,
        id_user_responsable: mermaFormData.id_user_responsable || 1,
        observacion: mermaFormData.observacion || null,
        estado: 'REGISTRADO',
        anulado: false
      };

      try {
        const response = await fetch(`${API_BASE_URL}/v1/mermas/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mermaData),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.data || 'Error al registrar la merma');
        }

        toast.success(`Merma registrada: ${mermaFormData.cantidad} ${insumo.unidad_medida} de ${insumo.nombre}`);
        await fetchMermas();
        await fetchInsumos(); // Actualizar stock de insumos
        setIsMermaDialogOpen(false);
        resetMermaForm();
      } catch (error: any) {
        console.error("Error al registrar merma de insumo:", error);
        toast.error(error.message || "Error al registrar la merma");
      }
    } else {
      // Validación para productos
      if (!mermaFormData.id_producto || !mermaFormData.cantidad || mermaFormData.cantidad <= 0) {
        toast.error("Selecciona un producto y cantidad válida");
        return;
      }

      const producto = products.find(p => p.id_producto === mermaFormData.id_producto);
      if (!producto) {
        toast.error("Producto no encontrado");
        return;
      }

      if (mermaFormData.cantidad > producto.stock_actual) {
        toast.error(`Stock insuficiente. Disponible: ${producto.stock_actual}`);
        return;
      }

      const costoTotal = (mermaFormData.cantidad || 0) * (mermaFormData.costo_unitario || 0);

      const mermaData = {
        numero_registro: generateMermaNumber(),
        tipo: mermaFormData.tipo,
        causa: mermaFormData.causa || `Merma por ${mermaFormData.tipo?.toLowerCase()}`,
        cantidad: mermaFormData.cantidad,
        costo_unitario: mermaFormData.costo_unitario,
        costo_total: costoTotal,
        fecha_caso: new Date().toISOString(),
        id_insumo: null,
        id_producto: mermaFormData.id_producto,
        id_lote: null,
        id_user_responsable: mermaFormData.id_user_responsable || 1,
        observacion: mermaFormData.observacion || null,
        estado: 'REGISTRADO',
        anulado: false
      };

      try {
        const response = await fetch(`${API_BASE_URL}/v1/mermas/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mermaData),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.data || 'Error al registrar la merma');
        }

        toast.success(`Merma registrada: ${mermaFormData.cantidad} unidades de ${producto.nombre}`);
        await fetchMermas();
        await fetchProducts(); // Actualizar stock
        setIsMermaDialogOpen(false);
        resetMermaForm();
      } catch (error: any) {
        console.error("Error al registrar merma:", error);
        toast.error(error.message || "Error al registrar la merma");
      }
    }
  };

  const resetMermaForm = () => {
    setMermaFormData({
      tipo: 'PRODUCCION',
      tipoItem: 'insumo',
      causa: '',
      cantidad: 0,
      costo_unitario: 0,
      costo_total: 0,
      fecha_caso: new Date().toISOString().split('T')[0],
      id_producto: null,
      id_insumo: null,
      id_user_responsable: 1,
      observacion: ''
    });
  };

  const getMermaTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'VENCIMIENTO': return 'bg-red-100 text-red-800';
      case 'HONGEADO': return 'bg-yellow-100 text-yellow-800';
      case 'DAÑO': return 'bg-orange-100 text-orange-800';
      case 'PRODUCCION': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMermaTipoLabel = (tipo: string) => {
    switch (tipo) {
      case 'VENCIMIENTO': return 'Vencimiento';
      case 'HONGEADO': return 'Hongeado';
      case 'DAÑO': return 'Daño';
      case 'PRODUCCION': return 'Producción';
      default: return tipo;
    }
  };

  // Filtrar mermas
  const filteredMermas = mermas.filter(merma => {
    const matchesSearch = merma.numero_registro.toLowerCase().includes(mermaSearchTerm.toLowerCase()) ||
                         merma.causa?.toLowerCase().includes(mermaSearchTerm.toLowerCase());
    const matchesTipo = selectedMermaTipo === "all" || merma.tipo === selectedMermaTipo;
    return matchesSearch && matchesTipo && !merma.anulado;
  });

  // Paginación de mermas
  const {
    currentPage: mermaCurrentPage,
    setCurrentPage: setMermaCurrentPage,
    itemsPerPage: mermaItemsPerPage,
    setItemsPerPage: setMermaItemsPerPage,
    totalPages: mermaTotalPages,
    totalItems: mermaTotalItems,
    paginatedItems: paginatedMermas,
  } = usePagination(filteredMermas, 10);

  // Estadísticas de mermas
  const mermaStats = {
    total: mermas.filter(m => !m.anulado).length,
    porVencimiento: mermas.filter(m => m.tipo === 'VENCIMIENTO' && !m.anulado).length,
    porHongeado: mermas.filter(m => m.tipo === 'HONGEADO' && !m.anulado).length,
    porDano: mermas.filter(m => m.tipo === 'DAÑO' && !m.anulado).length,
    porProduccion: mermas.filter(m => m.tipo === 'PRODUCCION' && !m.anulado).length,
    costoTotal: mermas.filter(m => !m.anulado).reduce((sum, m) => sum + (m.costo_total || 0), 0),
  };

  // ============ FIN FUNCIONES DE MERMAS ============

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
      </div>

      {/* Tabs para Productos y Mermas */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="productos" className="flex items-center gap-2">
            <Package className="h-4 w-4" />
            Productos
          </TabsTrigger>
          <TabsTrigger value="mermas" className="flex items-center gap-2">
            <FileWarning className="h-4 w-4" />
            Mermas
            {mermaStats.total > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs">{mermaStats.total}</Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Tab de Productos */}
        <TabsContent value="productos" className="space-y-6 mt-6">
          {/* Botones de acción de productos */}
          <div className="flex flex-wrap gap-2">
            <Button onClick={openProductionDialogWithRecipe}>
              <ChefHat className="h-4 w-4 mr-2" />
              Producir
            </Button>
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
                {paginatedProducts.map((product) => {
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
                        <div className="font-medium">{formatNumber(product.stock_actual)} {product.unidad_medida?.toLowerCase()}</div>
                        <div className="text-xs text-muted-foreground">
                          Mínimo: {formatNumber(product.stock_minimo)}
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
          
          {/* Paginación */}
          <TablePagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            itemsPerPage={itemsPerPage}
            onPageChange={setCurrentPage}
            onItemsPerPageChange={setItemsPerPage}
          />
        </CardContent>
      </Card>
        </TabsContent>

        {/* Tab de Mermas */}
        <TabsContent value="mermas" className="space-y-6 mt-6">
          {/* Estadísticas de Mermas */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Mermas</p>
                    <p className="text-2xl font-bold">{mermaStats.total}</p>
                  </div>
                  <FileWarning className="h-5 w-5 text-gray-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Vencimiento</p>
                    <p className="text-2xl font-bold text-orange-600">{mermaStats.porVencimiento}</p>
                  </div>
                  <Calendar className="h-5 w-5 text-orange-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Hongeado</p>
                    <p className="text-2xl font-bold text-green-600">{mermaStats.porHongeado}</p>
                  </div>
                  <TrendingDown className="h-5 w-5 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Daño</p>
                    <p className="text-2xl font-bold text-red-600">{mermaStats.porDano}</p>
                  </div>
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Producción</p>
                    <p className="text-2xl font-bold text-blue-600">{mermaStats.porProduccion}</p>
                  </div>
                  <ChefHat className="h-5 w-5 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Costo Total</p>
                    <p className="text-2xl font-bold text-red-600">S/ {mermaStats.costoTotal.toFixed(2)}</p>
                  </div>
                  <DollarSign className="h-5 w-5 text-red-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filtros de Mermas */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar mermas..."
                    value={mermaSearchTerm}
                    onChange={(e) => setMermaSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                
                <Select value={selectedMermaTipo} onValueChange={setSelectedMermaTipo}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Tipo de Merma" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los tipos</SelectItem>
                    <SelectItem value="VENCIMIENTO">Vencimiento</SelectItem>
                    <SelectItem value="HONGEADO">Hongeado</SelectItem>
                    <SelectItem value="DAÑO">Daño</SelectItem>
                    <SelectItem value="PRODUCCION">Producción</SelectItem>
                  </SelectContent>
                </Select>

                <Button onClick={() => openMermaDialog()}>
                  <Plus className="h-4 w-4 mr-2" />
                  Registrar Merma
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Tabla de Mermas */}
          <Card>
            <CardHeader>
              <CardTitle>Registro de Mermas</CardTitle>
              <CardDescription>
                {filteredMermas.length} mermas encontradas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>N° Registro</TableHead>
                      <TableHead>Producto</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Cantidad</TableHead>
                      <TableHead>Costo Total</TableHead>
                      <TableHead>Fecha</TableHead>
                      <TableHead>Causa</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedMermas.map((merma) => {
                      const producto = merma.id_producto ? products.find(p => p.id_producto === merma.id_producto) : null;
                      const insumo = merma.id_insumo ? insumos.find(i => i.id_insumo === merma.id_insumo) : null;
                      const esInsumo = !!merma.id_insumo;
                      
                      return (
                        <TableRow key={merma.id_merma}>
                          <TableCell>
                            <span className="font-mono text-sm">{merma.numero_registro}</span>
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className={esInsumo ? "bg-purple-50 text-purple-700" : "bg-green-50 text-green-700"}>
                                  {esInsumo ? "Insumo" : "Producto"}
                                </Badge>
                                <span className="font-medium">
                                  {esInsumo ? insumo?.nombre : producto?.nombre || `#${merma.id_producto || merma.id_insumo}`}
                                </span>
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {esInsumo ? insumo?.codigo : producto?.codigo_producto}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge className={getMermaTipoColor(merma.tipo)}>
                              {getMermaTipoLabel(merma.tipo)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <span className="font-medium">
                              {merma.cantidad} {esInsumo ? insumo?.unidad_medida?.toLowerCase() : 'uds'}
                            </span>
                          </TableCell>
                          <TableCell>
                            <span className="font-medium text-red-600">S/ {(merma.costo_total || 0).toFixed(2)}</span>
                          </TableCell>
                          <TableCell>
                            <span className="text-sm">{new Date(merma.fecha_caso).toLocaleDateString()}</span>
                          </TableCell>
                          <TableCell>
                            <span className="text-sm text-muted-foreground">{merma.causa || '-'}</span>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                    {paginatedMermas.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                          No se encontraron mermas
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
              
              {/* Paginación de Mermas */}
              <TablePagination
                currentPage={mermaCurrentPage}
                totalPages={mermaTotalPages}
                totalItems={mermaTotalItems}
                itemsPerPage={mermaItemsPerPage}
                onPageChange={setMermaCurrentPage}
                onItemsPerPageChange={setMermaItemsPerPage}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

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
                    <SelectItem value="UNIDAD">UNIDAD</SelectItem>
                    <SelectItem value="KG">KG</SelectItem>
                    <SelectItem value="G">G</SelectItem>
                    <SelectItem value="L">L</SelectItem>
                    <SelectItem value="ML">ML</SelectItem>
                    <SelectItem value="CAJA">CAJA</SelectItem>
                    <SelectItem value="PAQUETE">PAQUETE</SelectItem>
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
                {movementData.type === 'venta' && selectedProduct && (
                  <p className="text-xs text-muted-foreground">
                    Stock disponible: {formatNumber(selectedProduct.stock_actual)}
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
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
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
                            <span className="font-medium">{product ? formatNumber(product.stock_actual) : 0} unidades</span>
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

      {/* Dialog para Sistema de Producción */}
      <Dialog open={isProductionDialogOpen} onOpenChange={setIsProductionDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <ChefHat className="h-5 w-5 mr-2" />
              Sistema de Producción
            </DialogTitle>
            <DialogDescription>
              Selecciona una receta, verifica el stock y ejecuta la producción
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Paso 1: Selección de receta y cantidad */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center">
                  <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">1</span>
                  Seleccionar Receta y Cantidad
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="receta-produccion">Receta a producir</Label>
                    <Select 
                      value={selectedRecipeId?.toString() || ""} 
                      onValueChange={handleRecipeSelection}
                    >
                      <SelectTrigger id="receta-produccion">
                        <SelectValue placeholder="Selecciona una receta" />
                      </SelectTrigger>
                      <SelectContent>
                        {recipes.length === 0 ? (
                          <div className="p-4 text-center text-muted-foreground">
                            No hay recetas disponibles
                          </div>
                        ) : (
                          recipes.map(recipe => (
                            <SelectItem key={recipe.id_receta} value={recipe.id_receta.toString()}>
                              {recipe.nombre_receta} (S/ {recipe.costo_estimado.toFixed(2)})
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="cantidad-batch">¿Cuántos lotes deseas producir?</Label>
                    <Input
                      id="cantidad-batch"
                      type="number"
                      min="1"
                      value={cantidadBatch}
                      onChange={(e) => {
                        setCantidadBatch(parseInt(e.target.value) || 1);
                        setValidacionStock(null);
                      }}
                    />
                    {selectedRecipeDetails && (
                      <div className="text-sm bg-blue-50 border border-blue-200 rounded-lg p-3 mt-2">
                        <p className="text-blue-800">
                          <strong>📦 1 lote = {selectedRecipeDetails.rendimiento_producto_terminado} {selectedRecipeDetails.rendimiento_producto_terminado === 1 ? 'unidad' : 'unidades'}</strong>
                        </p>
                        <p className="text-blue-600 mt-1">
                          Con <strong>{cantidadBatch} {cantidadBatch === 1 ? 'lote' : 'lotes'}</strong> producirás → <strong className="text-blue-800 text-base">{cantidadBatch * selectedRecipeDetails.rendimiento_producto_terminado} unidades</strong>
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Detalles de la receta seleccionada */}
                {selectedRecipeDetails && (
                  <div className="mt-4 p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-2 flex items-center">
                      <Package className="h-4 w-4 mr-2" />
                      Ingredientes necesarios
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                      {selectedRecipeDetails.detalles.map((detalle, index) => (
                        <div key={index} className="flex justify-between items-center text-sm p-2 bg-background rounded border">
                          <span>Insumo #{detalle.id_insumo}</span>
                          <span className="font-medium">{formatNumber(detalle.cantidad)} uds</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 pt-3 border-t flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Costo estimado total:</span>
                      <span className="font-semibold text-green-600">S/ {(selectedRecipeDetails.costo_estimado * cantidadBatch).toFixed(2)}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Paso 2: Validación de Stock */}
            <Card className={!selectedRecipeId ? 'opacity-50' : ''}>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center">
                  <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">2</span>
                  Validar Stock de Ingredientes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={validarStockProduccion} 
                  disabled={!selectedRecipeId || loadingValidation}
                  className="w-full mb-4"
                  variant="outline"
                >
                  {loadingValidation ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Verificando disponibilidad...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Validar Disponibilidad de Stock
                    </>
                  )}
                </Button>

                {validacionStock && (
                  <div className="space-y-4">
                    {/* Estado general */}
                    <div className={`p-3 rounded-lg flex items-center ${
                      validacionStock.puede_producir 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-red-50 border border-red-200'
                    }`}>
                      {validacionStock.puede_producir ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600 mr-2" />
                      )}
                      <div>
                        <span className={`font-medium ${validacionStock.puede_producir ? 'text-green-800' : 'text-red-800'}`}>
                          {validacionStock.puede_producir ? 'Stock Disponible' : 'Stock Insuficiente'}
                        </span>
                        <p className={`text-sm ${validacionStock.puede_producir ? 'text-green-600' : 'text-red-600'}`}>
                          {validacionStock.mensaje}
                        </p>
                      </div>
                    </div>

                    {/* Tabla de insumos */}
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Insumo</TableHead>
                          <TableHead className="text-right">Requerido</TableHead>
                          <TableHead className="text-right">Disponible</TableHead>
                          <TableHead className="text-center">Estado</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {validacionStock.insumos.map((insumo, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <div>
                                <div className="font-medium">{insumo.nombre_insumo}</div>
                                <div className="text-xs text-muted-foreground">{insumo.codigo_insumo}</div>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              {formatNumber(insumo.cantidad_requerida)} {insumo.unidad_medida}
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={insumo.es_suficiente ? 'text-green-600' : 'text-red-600'}>
                                {formatNumber(insumo.stock_disponible)} {insumo.unidad_medida}
                              </span>
                            </TableCell>
                            <TableCell className="text-center">
                              {insumo.es_suficiente ? (
                                <Badge className="bg-green-100 text-green-800">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  OK
                                </Badge>
                              ) : (
                                <Badge variant="destructive">
                                  <XCircle className="h-3 w-3 mr-1" />
                                  Falta {formatNumber(insumo.cantidad_requerida - insumo.stock_disponible)}
                                </Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Paso 3: Ejecutar Producción */}
            <Card className={!validacionStock?.puede_producir ? 'opacity-50' : ''}>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center">
                  <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">3</span>
                  Ejecutar Producción
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                  <p className="text-sm text-yellow-800">
                    <AlertTriangle className="h-4 w-4 inline mr-1" />
                    <strong>Importante:</strong> Al ejecutar la producción, se descontará automáticamente 
                    el stock de los insumos utilizando el método FEFO (primero en vencer, primero en salir).
                  </p>
                </div>

                {validacionStock?.puede_producir && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                    <p className="text-sm text-green-800">
                      <CheckCircle className="h-4 w-4 inline mr-1" />
                      <strong>{cantidadBatch} {cantidadBatch === 1 ? 'lote' : 'lotes'}</strong> × <strong>{selectedRecipeDetails?.rendimiento_producto_terminado || 1} uds/lote</strong> = 
                      <strong className="text-green-700 text-base ml-1">{cantidadBatch * (selectedRecipeDetails?.rendimiento_producto_terminado || 1)} unidades</strong> de 
                      <strong>{validacionStock.nombre_receta}</strong>
                    </p>
                  </div>
                )}

                <Button 
                  onClick={ejecutarProduccion}
                  disabled={!validacionStock?.puede_producir || loadingProduction}
                  className="w-full"
                >
                  {loadingProduction ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Procesando producción...
                    </>
                  ) : (
                    <>
                      <ChefHat className="h-4 w-4 mr-2" />
                      Ejecutar Producción
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={closeProductionDialog}>
              Cancelar
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog para Registro de Mermas */}
      <Dialog open={isMermaDialogOpen} onOpenChange={setIsMermaDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <FileWarning className="h-5 w-5 mr-2" />
              Registrar Merma
            </DialogTitle>
            <DialogDescription>
              Registra una pérdida de insumo o producto por producción, vencimiento, daño u otra causa
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleMermaSubmit} className="space-y-4">
            {/* Selector de tipo de item (Insumo o Producto) */}
            <div className="space-y-2">
              <Label>¿Qué tipo de merma registrar?</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={mermaFormData.tipoItem === 'insumo' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => setMermaFormData(prev => ({
                    ...prev,
                    tipoItem: 'insumo',
                    tipo: 'PRODUCCION',
                    id_producto: null,
                    id_insumo: null,
                    costo_unitario: 0,
                    cantidad: 0,
                    costo_total: 0
                  }))}
                >
                  <Package className="h-4 w-4 mr-2" />
                  Insumo (Materia Prima)
                </Button>
                <Button
                  type="button"
                  variant={mermaFormData.tipoItem === 'producto' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => setMermaFormData(prev => ({
                    ...prev,
                    tipoItem: 'producto',
                    tipo: 'VENCIMIENTO',
                    id_producto: null,
                    id_insumo: null,
                    costo_unitario: 0,
                    cantidad: 0,
                    costo_total: 0
                  }))}
                >
                  <ChefHat className="h-4 w-4 mr-2" />
                  Producto Terminado
                </Button>
              </div>
            </div>

            {/* Selector de Insumo o Producto según el tipo */}
            {mermaFormData.tipoItem === 'insumo' ? (
              <div className="space-y-2">
                <Label htmlFor="merma-insumo">Insumo</Label>
                <Select 
                  value={mermaFormData.id_insumo?.toString() || ""} 
                  onValueChange={(value: string) => {
                    const insumo = insumos.find(i => i.id_insumo === parseInt(value));
                    setMermaFormData(prev => ({
                      ...prev,
                      id_insumo: parseInt(value),
                      id_producto: null,
                      costo_unitario: insumo?.precio_promedio || 0
                    }));
                  }}
                >
                  <SelectTrigger id="merma-insumo">
                    <SelectValue placeholder="Selecciona un insumo" />
                  </SelectTrigger>
                  <SelectContent>
                    {insumos.filter(i => i.stock_actual > 0).map(insumo => (
                      <SelectItem key={insumo.id_insumo} value={insumo.id_insumo.toString()}>
                        {insumo.nombre} (Stock: {insumo.stock_actual} {insumo.unidad_medida})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="merma-producto">Producto</Label>
                <Select 
                  value={mermaFormData.id_producto?.toString() || ""} 
                  onValueChange={(value: string) => {
                    const producto = products.find(p => p.id_producto === parseInt(value));
                    setMermaFormData(prev => ({
                      ...prev,
                      id_producto: parseInt(value),
                      id_insumo: null,
                      costo_unitario: producto?.precio_venta || 0
                    }));
                  }}
                >
                  <SelectTrigger id="merma-producto">
                    <SelectValue placeholder="Selecciona un producto" />
                  </SelectTrigger>
                  <SelectContent>
                    {products.filter(p => p.stock_actual > 0).map(producto => (
                      <SelectItem key={producto.id_producto} value={producto.id_producto.toString()}>
                        {producto.nombre} (Stock: {producto.stock_actual})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="merma-tipo">Tipo de Merma</Label>
                <Select 
                  value={mermaFormData.tipo} 
                  onValueChange={(value: string) => setMermaFormData(prev => ({ ...prev, tipo: value }))}
                >
                  <SelectTrigger id="merma-tipo">
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PRODUCCION">Producción (uso extra)</SelectItem>
                    <SelectItem value="VENCIMIENTO">Vencimiento</SelectItem>
                    <SelectItem value="HONGEADO">Hongeado</SelectItem>
                    <SelectItem value="DAÑO">Daño</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="merma-cantidad">Cantidad</Label>
                <Input
                  id="merma-cantidad"
                  type="number"
                  min="0.01"
                  step="0.01"
                  max={
                    mermaFormData.tipoItem === 'insumo' 
                      ? insumos.find(i => i.id_insumo === mermaFormData.id_insumo)?.stock_actual || 999
                      : products.find(p => p.id_producto === mermaFormData.id_producto)?.stock_actual || 999
                  }
                  value={mermaFormData.cantidad || ""}
                  onChange={(e) => {
                    const cantidad = parseFloat(e.target.value) || 0;
                    setMermaFormData(prev => ({
                      ...prev,
                      cantidad,
                      costo_total: cantidad * (prev.costo_unitario || 0)
                    }));
                  }}
                  required
                />
                {mermaFormData.tipoItem === 'insumo' && mermaFormData.id_insumo && (
                  <p className="text-xs text-muted-foreground">
                    Unidad: {insumos.find(i => i.id_insumo === mermaFormData.id_insumo)?.unidad_medida}
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="merma-costo-unitario">Costo Unitario (S/)</Label>
                <Input
                  id="merma-costo-unitario"
                  type="number"
                  step="0.01"
                  value={mermaFormData.costo_unitario || ""}
                  onChange={(e) => {
                    const costo = parseFloat(e.target.value) || 0;
                    setMermaFormData(prev => ({
                      ...prev,
                      costo_unitario: costo,
                      costo_total: (prev.cantidad || 0) * costo
                    }));
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="merma-costo-total">Costo Total (S/)</Label>
                <Input
                  id="merma-costo-total"
                  type="number"
                  step="0.01"
                  value={mermaFormData.costo_total?.toFixed(2) || "0.00"}
                  disabled
                  className="bg-muted"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="merma-fecha">Fecha del Caso</Label>
              <Input
                id="merma-fecha"
                type="date"
                value={mermaFormData.fecha_caso}
                onChange={(e) => setMermaFormData(prev => ({ ...prev, fecha_caso: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="merma-causa">Causa</Label>
              <Input
                id="merma-causa"
                placeholder={mermaFormData.tipoItem === 'insumo' ? "Ej: Se usó más harina de lo normal al amasar..." : "Describe brevemente la causa..."}
                value={mermaFormData.causa}
                onChange={(e) => setMermaFormData(prev => ({ ...prev, causa: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="merma-observacion">Observaciones (opcional)</Label>
              <Textarea
                id="merma-observacion"
                placeholder="Observaciones adicionales..."
                value={mermaFormData.observacion}
                onChange={(e) => setMermaFormData(prev => ({ ...prev, observacion: e.target.value }))}
              />
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsMermaDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" variant="destructive">
                <FileWarning className="h-4 w-4 mr-2" />
                Registrar Merma
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}