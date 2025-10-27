import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, Building, Phone, Mail, MapPin, Star, Package } from "lucide-react";
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
import { Switch } from "./ui/switch";
import { API_BASE_URL } from "../constants";


interface SuppliedProduct {
  id: number;
  name: string;
  category: string;
  unitPrice: number;
  unit: string;
  quality: number; // 1-5 stars
  deliveryTime: number; // días
  minOrder: number;
}

// 1. Interfaces de Datos
interface Proveedor {
    id_proveedor: number;
    nombre: string;
    ruc_dni: string;
    numero_contacto: string;
    email_contacto: string;
    direccion_fiscal: string;
    anulado: boolean; 
    fecha_registro: string; // Para mostrar en la tabla
}

interface ProveedorFormData {
    nombre: string;
    ruc_dni: string;
    numero_contacto: string;
    email_contacto: string;
    direccion_fiscal: string;
}



export function SupplierManager() {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isProductDialogOpen, setIsProductDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Proveedor | null>(null); 
  const [selectedSupplier, setSelectedSupplier] = useState<Proveedor | null>(null); 
  const [formData, setFormData] = useState<Partial<Proveedor>>({}); 
  const [productFormData, setProductFormData] = useState<Partial<SuppliedProduct>>({});

  const fetchProveedores = async () => {
    try {
        // 🚨 URL VERIFICADA: /api/v1/proveedores/ (en plural)
        const response = await fetch(`${API_BASE_URL}/v1/proveedores/`, { 
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`Error al cargar proveedores: ${response.statusText}`);
        }

        const responseData = await response.json();
        
        if (responseData.success && Array.isArray(responseData.data)) {
            
            const loadedProveedores = responseData.data.map((p: any) => ({
                // 🚨 Mapeo del Backend (snake_case) al Frontend (camelCase) 🚨
                
                // Propiedades de la DB que coinciden:
                id: p.id_proveedor,                    // id_proveedor -> id
                companyName: p.nombre,                 // nombre -> companyName
                contactName: p.nombre,                 // Usamos 'nombre' de nuevo, asumiendo que es el nombre de la empresa/contacto
                email: p.email_contacto,               // email_contacto -> email
                phone: p.numero_contacto,              // numero_contacto -> phone
                city: p.direccion_fiscal.split(',')[0] || "N/A", // Parsea la dirección
                state: p.direccion_fiscal.split(',').pop() || "N/A", // Parsea la dirección

                // Propiedades de la DB que deben ser invertidas/traducidas:
                isActive: !p.anulado,                  // !anulado -> isActive

                // ⚠️ Propiedades Faltantes (usa valores por defecto para que no falle el JSX):
                preferredSupplier: false,
                category: "General",
                rating: 0,
                suppliedProducts: [], // Lista vacía, si no tienes el endpoint de productos
                totalAmount: 0,
                totalOrders: 0,
                paymentTerms: "30 días",
                
            })); // Asignar el tipo de dato si es necesario

            setProveedores(loadedProveedores); // Guarda la lista mapeada en 'proveedores'
        }

    } catch (error) {
        console.error("Fallo la conexión con el Backend para proveedores:", error);
        // Opcional: Mostrar un mensaje de error en el UI
    }
  };

  const supplierCategories = [
    'all',
    'Ingredientes',
    'Empaques',
    'Servicios',
    'Equipos',
    // Agrega más categorías si es necesario
];

const paymentTermsOptions = [
    { value: '7 días', label: '7 días (Pronto Pago)' },
    { value: '15 días', label: '15 días' },
    { value: '30 días', label: '30 días' },
    { value: '45 días', label: '45 días (Estándar)' },
    { value: '60 días', label: '60 días (Crédito Extendido)' },
];

 // Lógica de Filtrado Corregida
const filteredSuppliers = proveedores.filter(proveedor => { // 🚨 suppliers -> proveedores
  const matchesSearch = proveedor.companyName.toLowerCase().includes(searchTerm.toLowerCase()) || // 🚨 supplier -> proveedor
                        proveedor.contactName.toLowerCase().includes(searchTerm.toLowerCase());  // 🚨 supplier -> proveedor
  const matchesCategory = selectedCategory === "all" || proveedor.category === selectedCategory; // 🚨 supplier -> proveedor
  return matchesSearch && matchesCategory;
});

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  
  if (editingSupplier) {
    setProveedores(prev => // 🚨 setSuppliers -> setProveedores
      prev.map(proveedor => // 🚨 supplier -> proveedor
        proveedor.id === editingSupplier.id 
          ? { ...proveedor, ...formData } as Proveedor // 🚨 Supplier -> Proveedor
          : proveedor
      )
    );
  } else {
    const newSupplier: Proveedor = { // 🚨 Supplier -> Proveedor
      id: Math.max(...proveedores.map(s => s.id)) + 1, // 🚨 suppliers -> proveedores
      ...formData,
      isActive: true,
      rating: 0,
      totalOrders: 0,
      totalAmount: 0,
      lastOrderDate: '',
      registrationDate: new Date().toISOString().split('T')[0],
      suppliedProducts: []
    } as Proveedor; // 🚨 Supplier -> Proveedor
    setProveedores(prev => [...prev, newSupplier]); // 🚨 setSuppliers -> setProveedores
  }
  
  setIsDialogOpen(false);
  setEditingSupplier(null);
  setFormData({});
};

const handleProductSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!selectedSupplier) return;

  const newProduct: SuppliedProduct = {
    id: Date.now(),
    ...productFormData
  } as SuppliedProduct;

  setProveedores(prev => // 🚨 setSuppliers -> setProveedores
    prev.map(proveedor => // 🚨 supplier -> proveedor
      proveedor.id === selectedSupplier.id
        ? { ...proveedor, suppliedProducts: [...proveedor.suppliedProducts, newProduct] }
        : proveedor
    )
  );

  setIsProductDialogOpen(false);
  setSelectedSupplier(null);
  setProductFormData({});
};

const toggleSupplierStatus = (id: number) => {
  setProveedores(prev => // 🚨 setSuppliers -> setProveedores
    prev.map(proveedor => // 🚨 supplier -> proveedor
      proveedor.id === id ? { ...proveedor, isActive: !proveedor.isActive } : proveedor
    )
  );
};

const togglePreferredStatus = (id: number) => {
  setProveedores(prev => // 🚨 setSuppliers -> setProveedores
    prev.map(proveedor => // 🚨 supplier -> proveedor
      proveedor.id === id ? { ...proveedor, preferredSupplier: !proveedor.preferredSupplier } : proveedor
    )
  );
};

const handleEdit = (proveedor: Proveedor) => { // 🚨 supplier -> proveedor, Supplier -> Proveedor
  setEditingSupplier(proveedor);
  setFormData(proveedor);
  setIsDialogOpen(true);
};

const handleDelete = (id: number) => {
  setProveedores(prev => prev.filter(proveedor => proveedor.id !== id)); // 🚨 setSuppliers -> setProveedores, supplier -> proveedor
};

const openAddDialog = () => {
  setEditingSupplier(null);
  setFormData({ country: "México", paymentTerms: "30 días" });
  setIsDialogOpen(true);
};

const openAddProductDialog = (supplier: Proveedor) => { // 🚨 Supplier -> Proveedor
  setSelectedSupplier(supplier);
  setProductFormData({});
  setIsProductDialogOpen(true);
};

const renderStars = (rating: number) => {
  return Array.from({ length: 5 }, (_, i) => (
    <Star
      key={i}
      className={`h-4 w-4 ${i < Math.floor(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
    />
  ));
};

const getStatusBadge = (isActive: boolean) => {
  return isActive ? (
    <Badge className="bg-green-100 text-green-800">Activo</Badge>
  ) : (
    <Badge className="bg-red-100 text-red-800">Inactivo</Badge>
  );
};

// Estadísticas Corregidas
const stats = {
  total: proveedores.length, // 🚨 suppliers -> proveedores
  active: proveedores.filter(s => s.isActive).length, // 🚨 suppliers -> proveedores
  preferred: proveedores.filter(s => s.preferredSupplier).length, // 🚨 suppliers -> proveedores
  totalAmount: proveedores.reduce((sum, s) => sum + s.totalAmount, 0) // 🚨 suppliers -> proveedores
};

  useEffect(() => {
    fetchProveedores();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Proveedores</h2>
          <p className="text-muted-foreground">Administra tu red de proveedores y sus productos</p>
        </div>
        
        <Button onClick={openAddDialog}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Proveedor
        </Button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Proveedores</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Building className="h-5 w-5 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Proveedores Activos</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <Building className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Preferidos</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.preferred}</p>
              </div>
              <Star className="h-5 w-5 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Monto Total</p>
                <p className="text-2xl font-bold">${stats.totalAmount.toLocaleString()}</p>
              </div>
              <Package className="h-5 w-5 text-purple-500" />
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
                placeholder="Buscar proveedores..."
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
                {supplierCategories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de proveedores */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Proveedores</CardTitle>
          <CardDescription>
            {filteredSuppliers.length} proveedores encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Empresa</TableHead>
                  <TableHead>Contacto</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Calificación</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Productos</TableHead>
                  <TableHead>Total Compras</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSuppliers.map((supplier) => (
                  <TableRow key={supplier.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium flex items-center">
                          {supplier.companyName}
                          {supplier.preferredSupplier && (
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 ml-1" />
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">{supplier.city}, {supplier.state}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{supplier.contactName}</div>
                        <div className="text-sm text-muted-foreground flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {supplier.email}
                        </div>
                        <div className="text-sm text-muted-foreground flex items-center">
                          <Phone className="h-3 w-3 mr-1" />
                          {supplier.phone}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{supplier.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-1">
                        {renderStars(supplier.rating)}
                        <span className="text-sm text-muted-foreground ml-1">
                          ({supplier.rating.toFixed(1)})
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(supplier.isActive)}
                        <Switch
                          checked={supplier.isActive}
                          onCheckedChange={() => toggleSupplierStatus(supplier.id)}
                        />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-center">
                        <div className="font-medium">{supplier.suppliedProducts.length}</div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openAddProductDialog(supplier)}
                          className="mt-1"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Agregar
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">${supplier.totalAmount.toLocaleString()}</div>
                        <div className="text-sm text-muted-foreground">{supplier.totalOrders} órdenes</div>
                        <div className="text-xs text-muted-foreground">
                          {supplier.paymentTerms}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => togglePreferredStatus(supplier.id)}
                          className={supplier.preferredSupplier ? "text-yellow-600" : ""}
                        >
                          <Star className={`h-3 w-3 ${supplier.preferredSupplier ? 'fill-current' : ''}`} />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(supplier)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(supplier.id)}
                          className="text-red-600 hover:text-red-700"
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

      {/* Dialog para Proveedor */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingSupplier ? "Editar Proveedor" : "Nuevo Proveedor"}
            </DialogTitle>
            <DialogDescription>
              {editingSupplier ? "Modifica la información del proveedor" : "Registra un nuevo proveedor en el sistema"}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basic">Información Básica</TabsTrigger>
                <TabsTrigger value="contact">Contacto y Ubicación</TabsTrigger>
                <TabsTrigger value="business">Datos Comerciales</TabsTrigger>
              </TabsList>
              
              <TabsContent value="basic" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="companyName">Nombre de la Empresa</Label>
                    <Input
                      id="companyName"
                      placeholder="Ej: Distribuidora San Miguel S.A."
                      value={formData.companyName || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="contactName">Persona de Contacto</Label>
                    <Input
                      id="contactName"
                      placeholder="Ej: Carlos Hernández"
                      value={formData.contactName || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, contactName: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                        {supplierCategories.map(category => (
                          <SelectItem key={category} value={category}>{category}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="taxId">RFC/RUC</Label>
                    <Input
                      id="taxId"
                      placeholder="Ej: DSM850123ABC"
                      value={formData.taxId || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, taxId: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="website">Sitio Web (opcional)</Label>
                  <Input
                    id="website"
                    placeholder="https://www.empresa.com"
                    value={formData.website || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                  />
                </div>
              </TabsContent>

              <TabsContent value="contact" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Correo Electrónico</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="ventas@empresa.com"
                      value={formData.email || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="phone">Teléfono Principal</Label>
                    <Input
                      id="phone"
                      placeholder="+1234567890"
                      value={formData.phone || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="alternatePhone">Teléfono Alternativo</Label>
                  <Input
                    id="alternatePhone"
                    placeholder="+1234567891"
                    value={formData.alternatePhone || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, alternatePhone: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Dirección</Label>
                  <Input
                    id="address"
                    placeholder="Av. Industrial 1250"
                    value={formData.address || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">Ciudad</Label>
                    <Input
                      id="city"
                      placeholder="Ciudad de México"
                      value={formData.city || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="state">Estado/Provincia</Label>
                    <Input
                      id="state"
                      placeholder="CDMX"
                      value={formData.state || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="postalCode">Código Postal</Label>
                    <Input
                      id="postalCode"
                      placeholder="11000"
                      value={formData.postalCode || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, postalCode: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="country">País</Label>
                    <Input
                      id="country"
                      placeholder="México"
                      value={formData.country || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, country: e.target.value }))}
                      required
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="business" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="paymentTerms">Términos de Pago</Label>
                    <Select 
                      value={formData.paymentTerms || ""} 
                      onValueChange={(value) => setFormData(prev => ({ ...prev, paymentTerms: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona términos" />
                      </SelectTrigger>
                      <SelectContent>
                        {paymentTermsOptions.map(term => (
                          <SelectItem key={term} value={term}>{term}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="deliveryZone">Zona de Entrega</Label>
                    <Input
                      id="deliveryZone"
                      placeholder="Centro y Norte"
                      value={formData.deliveryZone || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, deliveryZone: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Notas</Label>
                  <Textarea
                    id="notes"
                    placeholder="Información adicional sobre el proveedor..."
                    value={formData.notes || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                    rows={4}
                  />
                </div>
              </TabsContent>
            </Tabs>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingSupplier ? "Actualizar" : "Crear Proveedor"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Dialog para Productos del Proveedor */}
      <Dialog open={isProductDialogOpen} onOpenChange={setIsProductDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Agregar Producto</DialogTitle>
            <DialogDescription>
              Agregar producto a {selectedSupplier?.companyName}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleProductSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="productName">Nombre del Producto</Label>
                <Input
                  id="productName"
                  placeholder="Ej: Harina de Trigo Premium"
                  value={productFormData.name || ""}
                  onChange={(e) => setProductFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="productCategory">Categoría</Label>
                <Input
                  id="productCategory"
                  placeholder="Ej: Harinas"
                  value={productFormData.category || ""}
                  onChange={(e) => setProductFormData(prev => ({ ...prev, category: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="unitPrice">Precio Unitario</Label>
                <Input
                  id="unitPrice"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={productFormData.unitPrice || ""}
                  onChange={(e) => setProductFormData(prev => ({ ...prev, unitPrice: parseFloat(e.target.value) }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="unit">Unidad</Label>
                <Select 
                  value={productFormData.unit || ""} 
                  onValueChange={(value) => setProductFormData(prev => ({ ...prev, unit: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Unidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="kg">Kilogramo (kg)</SelectItem>
                    <SelectItem value="g">Gramo (g)</SelectItem>
                    <SelectItem value="litro">Litro</SelectItem>
                    <SelectItem value="ml">Mililitro (ml)</SelectItem>
                    <SelectItem value="unidades">Unidades</SelectItem>
                    <SelectItem value="docena">Docena</SelectItem>
                    <SelectItem value="caja">Caja</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="minOrder">Orden Mínima</Label>
                <Input
                  id="minOrder"
                  type="number"
                  placeholder="0"
                  value={productFormData.minOrder || ""}
                  onChange={(e) => setProductFormData(prev => ({ ...prev, minOrder: parseInt(e.target.value) }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quality">Calidad (1-5 estrellas)</Label>
                <Select 
                  value={productFormData.quality?.toString() || ""} 
                  onValueChange={(value) => setProductFormData(prev => ({ ...prev, quality: parseInt(value) }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Calidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 estrella</SelectItem>
                    <SelectItem value="2">2 estrellas</SelectItem>
                    <SelectItem value="3">3 estrellas</SelectItem>
                    <SelectItem value="4">4 estrellas</SelectItem>
                    <SelectItem value="5">5 estrellas</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="deliveryTime">Tiempo de Entrega (días)</Label>
                <Input
                  id="deliveryTime"
                  type="number"
                  min="1"
                  placeholder="0"
                  value={productFormData.deliveryTime || ""}
                  onChange={(e) => setProductFormData(prev => ({ ...prev, deliveryTime: parseInt(e.target.value) }))}
                  required
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsProductDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                Agregar Producto
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}