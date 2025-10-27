import { useState, useEffect } from "react";
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
  id: number;
  name: string;
  recipeId: number;
  recipeName: string;
  category: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  unitCost: number;
  sellingPrice: number;
  profitMargin: number;
  expiryDate: string;
  productionDate: string;
  batchNumber: string;
  barcode?: string;
  description: string;
  status: 'Disponible' | 'Agotado' | 'Por Vencer';
  movements: ProductMovement[];
}

// Mock data de recetas disponibles
const availableRecipes = [
  { id: 1, name: "Pastel de Chocolate Clásico", costPerServing: 0.71, category: "Pasteles" },
  { id: 2, name: "Galletas de Mantequilla", costPerServing: 0.08, category: "Galletas" },
  { id: 3, name: "Pan Integral", costPerServing: 0.35, category: "Panes" },
  { id: 4, name: "Cheesecake de Fresa", costPerServing: 1.25, category: "Postres" },
];


 
// Sistema de promociones automáticas
const generatePromotionSuggestions = (products: FinishedProduct[]): PromotionSuggestion[] => {
  const suggestions: PromotionSuggestion[] = [];
  const today = new Date();
  
  products.forEach(product => {
    const expiryDate = new Date(product.expiryDate);
    const daysUntilExpiry = Math.ceil((expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiry <= 3 && product.currentStock > 0) {
      // Sugerencia de descuento directo
      const suggestedDiscount = daysUntilExpiry <= 1 ? 40 : daysUntilExpiry <= 2 ? 25 : 15;
      suggestions.push({
        id: suggestions.length + 1,
        productId: product.id,
        type: 'discount',
        title: `Descuento ${suggestedDiscount}% - ${product.name}`,
        description: `Aplicar ${suggestedDiscount}% de descuento por vencimiento en ${daysUntilExpiry} día(s)`,
        suggestedDiscount,
        daysUntilExpiry,
        potentialSavings: product.currentStock * product.unitCost * (suggestedDiscount / 100),
        isActive: false
      });
      
      // Sugerencia de combo con productos complementarios
      const complementaryProducts = products.filter(p => 
        p.id !== product.id && 
        p.currentStock > 0 && 
        (p.category === product.category || isComplementaryCategory(p.category, product.category))
      );
      
      if (complementaryProducts.length > 0) {
        const comboProduct = complementaryProducts[0];
        suggestions.push({
          id: suggestions.length + 1,
          productId: product.id,
          type: 'combo',
          title: `Combo Especial: ${product.name} + ${comboProduct.name}`,
          description: `Combo de ${product.name} (por vencer) con ${comboProduct.name} - Precio especial`,
          comboProducts: [product.id, comboProduct.id],
          daysUntilExpiry,
          potentialSavings: product.currentStock * product.unitCost * 0.3, // 30% de las pérdidas
          isActive: false
        });
      }
      
      // Sugerencia de liquidación urgente
      if (daysUntilExpiry <= 1) {
        suggestions.push({
          id: suggestions.length + 1,
          productId: product.id,
          type: 'clearance',
          title: `¡LIQUIDACIÓN URGENTE! - ${product.name}`,
          description: `Venta de liquidación - Vence mañana. Precio especial para evitar merma total`,
          suggestedDiscount: 50,
          daysUntilExpiry,
          potentialSavings: product.currentStock * product.unitCost * 0.5,
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
  const [products, setProducts] = useState<FinishedProduct[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isMovementDialogOpen, setIsMovementDialogOpen] = useState(false);
  const [isPromotionDialogOpen, setIsPromotionDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<FinishedProduct | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<FinishedProduct | null>(null);
  const [formData, setFormData] = useState<Partial<FinishedProduct>>({});
  const [movementData, setMovementData] = useState<Partial<ProductMovement>>({});
  const [promotionSuggestions, setPromotionSuggestions] = useState<PromotionSuggestion[]>([]);
  const [selectedPromotion, setSelectedPromotion] = useState<PromotionSuggestion | null>(null);

  
  const categories = ["Pasteles", "Galletas", "Panes", "Postres", "Decoraciones"];

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
                // Mapeo de DB (snake_case) a React (camelCase)
                id: p.id_producto,               
                name: p.nombre,                   
                currentStock: parseFloat(p.stock_actual || 0),
                minStock: parseFloat(p.stock_minimo || 0),   
                sellingPrice: parseFloat(p.precio_venta || 0),
                description: p.descripcion || "",
                
                // Valores de relleno necesarios para que la interfaz NO falle
                recipeName: p.nombre_receta || "N/A",  // Si tienes este campo en tu API, úsalo
                category: p.categoria || "Sin Categoría",
                unitCost: parseFloat(p.costo_unitario || 0), // Si lo agregaste en la DB
                profitMargin: 0.00, // Debe ser calculado: (sellingPrice - unitCost) / unitCost
                expiryDate: p.fecha_vencimiento || new Date().toISOString().split('T')[0],
                productionDate: p.fecha_produccion || new Date().toISOString().split('T')[0],
                batchNumber: p.codigo_producto || "N/A",
                status: 'Disponible', // O una función para calcular el estado
                maxStock: 20,
                recipeId: 0,
                movements: [],
            })) as FinishedProduct[];
            
            setProducts(loadedProducts);
        }

    } catch (error) {
        console.error("Fallo la carga de productos. El error es:", error);
    }
};

useEffect(() => {
        // Llama a la función que realiza la petición a la API
        fetchProducts(); 
    }, []); // El array vacío '[]' es crucial para que se ejecute solo al inicio.

  // Generar sugerencias de promociones automáticamente
  useState(() => {
    setPromotionSuggestions(generatePromotionSuggestions(products));
  });

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.recipeName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || product.category === selectedCategory;
    const matchesStatus = selectedStatus === "all" || product.status === selectedStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Disponible': return 'bg-green-100 text-green-800';
      case 'Agotado': return 'bg-red-100 text-red-800';
      case 'Por Vencer': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const generateBatchNumber = (recipeId: number) => {
    const today = new Date();
    const dateStr = today.toISOString().slice(2, 10).replace(/-/g, '');
    const recipe = availableRecipes.find(r => r.id === recipeId);
    const prefix = recipe?.name.substring(0, 2).toUpperCase() || 'PR';
    const sequence = '001'; // En una implementación real, esto sería incremental
    return `${prefix}${dateStr}${sequence}`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const selectedRecipe = availableRecipes.find(r => r.id === formData.recipeId);
    const batchNumber = formData.batchNumber || generateBatchNumber(formData.recipeId || 0);
    
    if (editingProduct) {
      setProducts(prev => 
        prev.map(product => 
          product.id === editingProduct.id 
            ? { 
                ...product, 
                ...formData,
                recipeName: selectedRecipe?.name || product.recipeName,
                profitMargin: formData.sellingPrice && formData.unitCost ? 
                  ((formData.sellingPrice - formData.unitCost) / formData.unitCost) * 100 : 
                  product.profitMargin
              } as FinishedProduct
            : product
        )
      );
    } else {
      const newProduct: FinishedProduct = {
        id: Math.max(...products.map(p => p.id)) + 1,
        ...formData,
        recipeName: selectedRecipe?.name || "",
        batchNumber,
        status: 'Disponible',
        movements: [],
        profitMargin: formData.sellingPrice && formData.unitCost ? 
          ((formData.sellingPrice - formData.unitCost) / formData.unitCost) * 100 : 0
      } as FinishedProduct;
      setProducts(prev => [...prev, newProduct]);
    }
    
    setIsDialogOpen(false);
    setEditingProduct(null);
    setFormData({});
  };

  const handleMovementSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedProduct || !movementData.type || !movementData.quantity) return;

    const newMovement: ProductMovement = {
      id: Date.now(),
      type: movementData.type,
      quantity: movementData.quantity,
      date: movementData.date || new Date().toISOString().split('T')[0],
      notes: movementData.notes,
      batchNumber: selectedProduct.batchNumber
    };

    setProducts(prev =>
      prev.map(product => {
        if (product.id === selectedProduct.id) {
          const updatedStock = movementData.type === 'produccion' 
            ? product.currentStock + movementData.quantity
            : product.currentStock - movementData.quantity;
          
          const newStatus = updatedStock <= 0 ? 'Agotado' : 
                           updatedStock <= product.minStock ? 'Por Vencer' : 'Disponible';

          return {
            ...product,
            currentStock: Math.max(0, updatedStock),
            status: newStatus,
            movements: [...product.movements, newMovement]
          };
        }
        return product;
      })
    );

    setIsMovementDialogOpen(false);
    setSelectedProduct(null);
    setMovementData({});
  };

  const openProductionDialog = (product: FinishedProduct) => {
    setSelectedProduct(product);
    setMovementData({ type: 'produccion', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
  };

  const openSaleDialog = (product: FinishedProduct) => {
    setSelectedProduct(product);
    setMovementData({ type: 'venta', date: new Date().toISOString().split('T')[0] });
    setIsMovementDialogOpen(true);
  };

  const handleEdit = (product: FinishedProduct) => {
    setEditingProduct(product);
    setFormData(product);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    setProducts(prev => prev.filter(product => product.id !== id));
  };

  const openAddDialog = () => {
    setEditingProduct(null);
    setFormData({
      productionDate: new Date().toISOString().split('T')[0],
      minStock: 5,
      maxStock: 20
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

  // Estadísticas
  const stats = {
    total: products.length,
    available: products.filter(p => p.status === 'Disponible').length,
    outOfStock: products.filter(p => p.status === 'Agotado').length,
    expiring: products.filter(p => p.status === 'Por Vencer').length,
    totalValue: products.reduce((sum, p) => sum + (p.currentStock * p.sellingPrice), 0),
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
          <Button onClick={openAddDialog}>
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Producto
          </Button>
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
                <p className="text-sm text-muted-foreground">Por Vencer</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.expiring}</p>
              </div>
              <Calendar className="h-5 w-5 text-yellow-500" />
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
                  <TableHead>Producto</TableHead>
                  <TableHead>Receta Base</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Costo/Precio</TableHead>
                  <TableHead>Margen</TableHead>
                  <TableHead>Vencimiento</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.name}</div>
                        <div className="text-sm text-muted-foreground">{product.batchNumber}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.recipeName}</div>
                        <div className="text-sm text-muted-foreground">{product.category}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.currentStock} unidades</div>
                        <div className="text-xs text-muted-foreground">
                          Min: {product.minStock} | Max: {product.maxStock}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(product.status)}>
                        {product.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="text-sm">Costo: ${product.unitCost.toFixed(2)}</div>
                        <div className="font-medium">Precio: ${product.sellingPrice.toFixed(2)}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={`font-medium ${
                        product.profitMargin > 100 ? 'text-green-600' : 
                        product.profitMargin > 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {product.profitMargin.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div>{new Date(product.expiryDate).toLocaleDateString()}</div>
                        <div className="text-xs text-muted-foreground">
                          Prod: {new Date(product.productionDate).toLocaleDateString()}
                        </div>
                      </div>
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
                          disabled={product.currentStock <= 0}
                        >
                          <DollarSign className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(product)}
                        >
                          <Edit className="h-3 w-3" />
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

      {/* Dialog para nuevo/editar producto */}
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
                <Label htmlFor="name">Nombre del Producto</Label>
                <Input
                  id="name"
                  placeholder="Ej: Pastel de Chocolate Premium"
                  value={formData.name || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="recipeId">Receta Base</Label>
                <Select 
                  value={formData.recipeId?.toString() || ""} 
                  onValueChange={(value) => {
                    const recipeId = parseInt(value);
                    const recipe = availableRecipes.find(r => r.id === recipeId);
                    setFormData(prev => ({ 
                      ...prev, 
                      recipeId,
                      category: recipe?.category || prev.category,
                      unitCost: recipe?.costPerServing || prev.unitCost
                    }));
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona receta" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableRecipes.map(recipe => (
                      <SelectItem key={recipe.id} value={recipe.id.toString()}>
                        {recipe.name} (${recipe.costPerServing.toFixed(2)})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descripción</Label>
              <Textarea
                id="description"
                placeholder="Descripción del producto..."
                value={formData.description || ""}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="currentStock">Stock Inicial</Label>
                <Input
                  id="currentStock"
                  type="number"
                  value={formData.currentStock || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, currentStock: parseInt(e.target.value) }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="minStock">Stock Mínimo</Label>
                <Input
                  id="minStock"
                  type="number"
                  value={formData.minStock || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, minStock: parseInt(e.target.value) }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="maxStock">Stock Máximo</Label>
                <Input
                  id="maxStock"
                  type="number"
                  value={formData.maxStock || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, maxStock: parseInt(e.target.value) }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="unitCost">Costo Unitario</Label>
                <Input
                  id="unitCost"
                  type="number"
                  step="0.01"
                  value={formData.unitCost || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, unitCost: parseFloat(e.target.value) }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="sellingPrice">Precio de Venta</Label>
                <Input
                  id="sellingPrice"
                  type="number"
                  step="0.01"
                  value={formData.sellingPrice || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, sellingPrice: parseFloat(e.target.value) }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="productionDate">Fecha de Producción</Label>
                <Input
                  id="productionDate"
                  type="date"
                  value={formData.productionDate || ""}
                  onChange={(e) => setFormData(prev => ({ ...prev, productionDate: e.target.value }))}
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
              {selectedProduct?.name} - Lote: {selectedProduct?.batchNumber}
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
                  max={movementData.type === 'venta' ? selectedProduct?.currentStock : undefined}
                  value={movementData.quantity || ""}
                  onChange={(e) => setMovementData(prev => ({ ...prev, quantity: parseInt(e.target.value) }))}
                  required
                />
                {movementData.type === 'venta' && (
                  <p className="text-xs text-muted-foreground">
                    Stock disponible: {selectedProduct?.currentStock}
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
                    const product = products.find(p => p.id === suggestion.productId);
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
                            <span className="font-medium">{product?.name}</span>
                          </div>
                          
                          <div className="flex justify-between text-sm">
                            <span>Stock actual:</span>
                            <span className="font-medium">{product?.currentStock} unidades</span>
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
                                  const comboProduct = products.find(p => p.id === productId);
                                  return (
                                    <Badge key={productId} variant="outline" className="mr-1 text-xs">
                                      {comboProduct?.name}
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
                    const product = products.find(p => p.id === suggestion.productId);
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

