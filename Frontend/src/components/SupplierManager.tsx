import { useState } from "react";
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

interface Supplier {
  id: number;
  companyName: string;
  contactName: string;
  email: string;
  phone: string;
  alternatePhone?: string;
  address: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  taxId: string; // RUC/RFC
  website?: string;
  category: string;
  rating: number; // 1-5 stars
  isActive: boolean;
  preferredSupplier: boolean;
  paymentTerms: string; // "Contado", "30 días", "60 días"
  deliveryZone: string;
  notes: string;
  registrationDate: string;
  lastOrderDate: string;
  totalOrders: number;
  totalAmount: number;
  suppliedProducts: SuppliedProduct[];
}

const supplierCategories = [
  "Ingredientes Básicos",
  "Productos Lácteos", 
  "Carnes y Proteínas",
  "Frutas y Verduras",
  "Especias y Condimentos",
  "Empaques y Envases",
  "Equipos y Utensilios",
  "Servicios"
];

const paymentTermsOptions = [
  "Contado",
  "15 días",
  "30 días",
  "45 días", 
  "60 días",
  "90 días"
];

const mockSuppliers: Supplier[] = [
  {
    id: 1,
    companyName: "Distribuidora San Miguel S.A.",
    contactName: "Carlos Hernández",
    email: "ventas@sanmiguel.com",
    phone: "+1234567890",
    alternatePhone: "+1234567891",
    address: "Av. Industrial 1250",
    city: "Ciudad de México",
    state: "CDMX",
    postalCode: "11000",
    country: "México",
    taxId: "DSM850123ABC",
    website: "www.sanmiguel.com",
    category: "Ingredientes Básicos",
    rating: 4.5,
    isActive: true,
    preferredSupplier: true,
    paymentTerms: "30 días",
    deliveryZone: "Centro y Norte",
    notes: "Proveedor confiable con excelente calidad en harinas y azúcares.",
    registrationDate: "2023-01-15",
    lastOrderDate: "2024-09-01",
    totalOrders: 45,
    totalAmount: 125000,
    suppliedProducts: [
      { id: 1, name: "Harina de Trigo Premium", category: "Harinas", unitPrice: 1.2, unit: "kg", quality: 5, deliveryTime: 2, minOrder: 50 },
      { id: 2, name: "Azúcar Refinada", category: "Azúcares", unitPrice: 2.5, unit: "kg", quality: 4, deliveryTime: 2, minOrder: 25 },
      { id: 3, name: "Sal Marina", category: "Condimentos", unitPrice: 0.8, unit: "kg", quality: 4, deliveryTime: 3, minOrder: 10 }
    ]
  },
  {
    id: 2,
    companyName: "Lácteos Premium LTDA",
    contactName: "María González",
    email: "pedidos@lacteospremium.com",
    phone: "+1234567892",
    address: "Carrera 15 #45-67",
    city: "Bogotá",
    state: "Cundinamarca",
    postalCode: "110111",
    country: "Colombia",
    taxId: "LPR901234567",
    category: "Productos Lácteos",
    rating: 4.8,
    isActive: true,
    preferredSupplier: true,
    paymentTerms: "15 días",
    deliveryZone: "Bogotá y alrededores",
    notes: "Excelente calidad en productos lácteos, entrega puntual.",
    registrationDate: "2023-03-20",
    lastOrderDate: "2024-09-02",
    totalOrders: 38,
    totalAmount: 89500,
    suppliedProducts: [
      { id: 4, name: "Mantequilla Sin Sal", category: "Lácteos", unitPrice: 8.5, unit: "kg", quality: 5, deliveryTime: 1, minOrder: 5 },
      { id: 5, name: "Leche Entera", category: "Lácteos", unitPrice: 1.8, unit: "litro", quality: 5, deliveryTime: 1, minOrder: 20 },
      { id: 6, name: "Crema de Leche", category: "Lácteos", unitPrice: 4.2, unit: "litro", quality: 4, deliveryTime: 1, minOrder: 10 }
    ]
  },
  {
    id: 3,
    companyName: "Empaques Modernos S.R.L.",
    contactName: "José Martínez",
    email: "info@empaquesmodernos.com",
    phone: "+1234567893",
    address: "Zona Industrial Km 12",
    city: "Guadalajara",
    state: "Jalisco",
    postalCode: "44100",
    country: "México",
    taxId: "EMP789012345",
    category: "Empaques y Envases",
    rating: 3.8,
    isActive: true,
    preferredSupplier: false,
    paymentTerms: "45 días",
    deliveryZone: "Nacional",
    notes: "Buenos precios en empaques, a veces hay retrasos en entrega.",
    registrationDate: "2023-06-10",
    lastOrderDate: "2024-08-25",
    totalOrders: 22,
    totalAmount: 35600,
    suppliedProducts: [
      { id: 7, name: "Cajas de Cartón 20x15x10", category: "Empaques", unitPrice: 0.45, unit: "unidad", quality: 4, deliveryTime: 5, minOrder: 100 },
      { id: 8, name: "Bolsas Plásticas Transparentes", category: "Empaques", unitPrice: 0.12, unit: "unidad", quality: 3, deliveryTime: 7, minOrder: 500 }
    ]
  }
];

export function SupplierManager() {
  const [suppliers, setSuppliers] = useState<Supplier[]>(mockSuppliers);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isProductDialogOpen, setIsProductDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [formData, setFormData] = useState<Partial<Supplier>>({});
  const [productFormData, setProductFormData] = useState<Partial<SuppliedProduct>>({});

  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = supplier.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         supplier.contactName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || supplier.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingSupplier) {
      setSuppliers(prev => 
        prev.map(supplier => 
          supplier.id === editingSupplier.id 
            ? { ...supplier, ...formData } as Supplier
            : supplier
        )
      );
    } else {
      const newSupplier: Supplier = {
        id: Math.max(...suppliers.map(s => s.id)) + 1,
        ...formData,
        isActive: true,
        rating: 0,
        totalOrders: 0,
        totalAmount: 0,
        lastOrderDate: '',
        registrationDate: new Date().toISOString().split('T')[0],
        suppliedProducts: []
      } as Supplier;
      setSuppliers(prev => [...prev, newSupplier]);
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

    setSuppliers(prev =>
      prev.map(supplier =>
        supplier.id === selectedSupplier.id
          ? { ...supplier, suppliedProducts: [...supplier.suppliedProducts, newProduct] }
          : supplier
      )
    );

    setIsProductDialogOpen(false);
    setSelectedSupplier(null);
    setProductFormData({});
  };

  const toggleSupplierStatus = (id: number) => {
    setSuppliers(prev =>
      prev.map(supplier =>
        supplier.id === id ? { ...supplier, isActive: !supplier.isActive } : supplier
      )
    );
  };

  const togglePreferredStatus = (id: number) => {
    setSuppliers(prev =>
      prev.map(supplier =>
        supplier.id === id ? { ...supplier, preferredSupplier: !supplier.preferredSupplier } : supplier
      )
    );
  };

  const handleEdit = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    setFormData(supplier);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    setSuppliers(prev => prev.filter(supplier => supplier.id !== id));
  };

  const openAddDialog = () => {
    setEditingSupplier(null);
    setFormData({ country: "México", paymentTerms: "30 días" });
    setIsDialogOpen(true);
  };

  const openAddProductDialog = (supplier: Supplier) => {
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

  // Estadísticas
  const stats = {
    total: suppliers.length,
    active: suppliers.filter(s => s.isActive).length,
    preferred: suppliers.filter(s => s.preferredSupplier).length,
    totalAmount: suppliers.reduce((sum, s) => sum + s.totalAmount, 0)
  };

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