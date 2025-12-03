import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, Phone, Mail, MapPin, Calendar, CheckCircle, XCircle } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "../context/AuthContext";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch"; // Importamos el Switch
import { API_BASE_URL } from "../constants";
import { TablePagination, usePagination } from "./ui/table-pagination";

// --- INTERFACES AJUSTADAS AL MODELO DE LA API ---

// Interfaz para la respuesta del GET y el estado local
interface Proveedor {
    id_proveedor: number;
    nombre: string;
    ruc_dni: string;
    numero_contacto: string;
    email_contacto: string;
    direccion_fiscal: string;
    anulado: boolean; // Presente en GET y PUT
    fecha_registro: string;
}

// Interfaz para el cuerpo del POST/PUT (solo los campos que se envían)
interface ProveedorFormData {
    nombre: string;
    ruc_dni: string;
    numero_contacto: string;
    email_contacto: string;
    direccion_fiscal: string;
    anulado: boolean; // CRÍTICO: Incluido para el PUT
}

// --- CONSTANTE DE URL ---
const PROVEEDORES_API_URL = `${API_BASE_URL}/v1/proveedores`;


export function SupplierManager() {
  const { canWrite } = useAuth();
  const canEditProveedores = canWrite('PROVEEDORES');
  
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingProveedorId, setEditingProveedorId] = useState<number | null>(null); 
  
  // Estado para el formulario con los campos exactos de la API
  const [formData, setFormData] = useState<ProveedorFormData>({
      nombre: "",
      ruc_dni: "",
      numero_contacto: "",
      email_contacto: "",
      direccion_fiscal: "",
      anulado: false, // Por defecto, no anulado (activo)
  });

  // --- LÓGICA DE API ---

  const fetchProveedores = async () => {
      let response;
      try {
          response = await fetch(`${PROVEEDORES_API_URL}/`, { 
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
          });

          if (!response.ok) {
              const errorBody = await response.text();
              throw new Error(`Error al cargar proveedores (Status: ${response.status}). Detalles: ${errorBody.substring(0, 100)}...`);
          }

          const responseData = await response.json();
          
          const rawData = responseData.data ? (Array.isArray(responseData.data) ? responseData.data : [responseData.data]) : [];
          
          const loadedProveedores: Proveedor[] = rawData.map((p: any) => ({
              id_proveedor: p.id_proveedor || 0,
              nombre: p.nombre || '',
              ruc_dni: p.ruc_dni || '',
              numero_contacto: p.numero_contacto || '',
              email_contacto: p.email_contacto || '',
              direccion_fiscal: p.direccion_fiscal || '',
              anulado: p.anulado || false,
              fecha_registro: p.fecha_registro || '',
          }));

          setProveedores(loadedProveedores);
      } catch (error) {
          console.error("Fallo la conexión con el Backend para proveedores:", error);
          setProveedores([]); 
      }
  };

  const createOrUpdateProveedor = async () => {
      const isEditing = editingProveedorId !== null;
      const url = isEditing ? `${PROVEEDORES_API_URL}/${editingProveedorId}` : PROVEEDORES_API_URL;
      // Tanto POST como PUT usan los campos de ProveedorFormData
      const method = isEditing ? 'PUT' : 'POST'; 
      
      // Para el POST, eliminamos 'anulado' del cuerpo si la API lo ignora, 
      // pero si el PUT lo requiere, lo mantenemos en formData para ser consistente.
      const bodyData = isEditing 
        ? formData 
        : { 
            nombre: formData.nombre,
            ruc_dni: formData.ruc_dni,
            numero_contacto: formData.numero_contacto,
            email_contacto: formData.email_contacto,
            direccion_fiscal: formData.direccion_fiscal,
            // 'anulado' se omite en POST si la API lo ignora o usa un valor por defecto.
            // Si el POST lo requiere, descomenta la línea de abajo:
            // anulado: formData.anulado, 
        };

      try {
          const response = await fetch(url, {
              method: method,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(bodyData), // Usamos el cuerpo ajustado
          });

          if (!response.ok) {
              const errorResult = await response.json();
              throw new Error(errorResult.message || `Error al ${isEditing ? 'actualizar' : 'crear'} el proveedor.`);
          }
          
          await fetchProveedores(); 
          setIsDialogOpen(false);
          setEditingProveedorId(null);
          setFormData({ nombre: "", ruc_dni: "", numero_contacto: "", email_contacto: "", direccion_fiscal: "", anulado: false });
      } catch (error) {
          console.error(`Error during ${method} operation:`, error);
          alert(`Operación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      }
  }

  // ... (handleDeleteAPI se mantiene igual, ya que solo requiere el ID)
  const handleDeleteAPI = async (id: number) => { 
      let response;
      try {
          response = await fetch(`${PROVEEDORES_API_URL}/${id}`, {
              method: 'DELETE',
          });
          
          if (!response.ok) {
              const errorResult = await response.json();
              throw new Error(errorResult.message || 'Error al eliminar el proveedor');
          }

          setProveedores(prev => prev.filter(p => p.id_proveedor !== id));
      } catch (error) {
          console.error("Error deleting supplier:", error);
          alert(`Eliminación fallida: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      }
  }; 
  
  // --- LÓGICA DE UI ---
  
  const handleEdit = (proveedor: Proveedor) => {
    setEditingProveedorId(proveedor.id_proveedor);
    // Mapea el objeto Proveedor a ProveedorFormData para el formulario, incluyendo 'anulado'
    setFormData({
        nombre: proveedor.nombre,
        ruc_dni: proveedor.ruc_dni,
        numero_contacto: proveedor.numero_contacto,
        email_contacto: proveedor.email_contacto,
        direccion_fiscal: proveedor.direccion_fiscal,
        anulado: proveedor.anulado, // Cargar el estado actual de anulación
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm("¿Está seguro que desea eliminar este proveedor?")) {
      handleDeleteAPI(id);
    }
  };

  const openAddDialog = () => {
    setEditingProveedorId(null);
    setFormData({ 
        nombre: "",
        ruc_dni: "",
        numero_contacto: "",
        email_contacto: "",
        direccion_fiscal: "",
        anulado: false, // Default para el nuevo registro
    });
    setIsDialogOpen(true);
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createOrUpdateProveedor();
  };

  useEffect(() => {
    fetchProveedores();
  }, []);

  // Filtrado simple por nombre o RUC/DNI
  const filteredSuppliers = proveedores.filter(proveedor => { 
    const searchLower = searchTerm.toLowerCase();
    return (
      proveedor.nombre.toLowerCase().includes(searchLower) ||
      proveedor.ruc_dni.toLowerCase().includes(searchLower) ||
      proveedor.email_contacto.toLowerCase().includes(searchLower)
    );
  });

  // Paginación
  const {
    currentPage,
    setCurrentPage,
    itemsPerPage,
    setItemsPerPage,
    totalPages,
    totalItems,
    paginatedItems: paginatedSuppliers,
  } = usePagination(filteredSuppliers, 10);

  const formatDate = (dateString: string) => {
      if (!dateString) return "N/A";
      try {
          return new Date(dateString).toLocaleDateString('es-ES', { 
              year: 'numeric', 
              month: 'short', 
              day: 'numeric' 
          });
      } catch {
          return dateString.split('T')[0];
      }
  };


  // --- RENDERIZADO DEL COMPONENTE (Actualizado) ---
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Proveedores</h2>
          <p className="text-muted-foreground">Administra los datos de contacto y fiscal de tus proveedores.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            {canEditProveedores && (
              <DialogTrigger asChild>
                  <Button onClick={openAddDialog}>
                      <Plus className="h-4 w-4 mr-2" />
                      Nuevo Proveedor
                  </Button>
              </DialogTrigger>
            )}
            
            <DialogContent className="max-w-xl">
              <DialogHeader>
                <DialogTitle>
                  {editingProveedorId ? "Editar Proveedor" : "Nuevo Proveedor"}
                </DialogTitle>
                <DialogDescription>
                  {editingProveedorId ? "Modifica la información del proveedor." : "Registra un nuevo proveedor en el sistema con la información de contacto y fiscal."}
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Campos de Contacto y Fiscal (Iguales para POST y PUT) */}
                <div className="space-y-2">
                  <Label htmlFor="nombre">Nombre / Razón Social</Label>
                  <Input
                    id="nombre"
                    placeholder="Ej: Distribuidora San Miguel S.A."
                    value={formData.nombre}
                    onChange={(e) => setFormData(prev => ({ ...prev, nombre: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="ruc_dni">RUC / DNI</Label>
                    <Input
                      id="ruc_dni"
                      placeholder="Ej: 10747089087"
                      value={formData.ruc_dni}
                      onChange={(e) => setFormData(prev => ({ ...prev, ruc_dni: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="numero_contacto">Teléfono</Label>
                    <Input
                      id="numero_contacto"
                      placeholder="Ej: 912345678"
                      value={formData.numero_contacto}
                      onChange={(e) => setFormData(prev => ({ ...prev, numero_contacto: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email_contacto">Correo Electrónico</Label>
                  <Input
                    id="email_contacto"
                    type="email"
                    placeholder="Ej: contacto@empresa.com"
                    value={formData.email_contacto}
                    onChange={(e) => setFormData(prev => ({ ...prev, email_contacto: e.target.value }))}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="direccion_fiscal">Dirección Fiscal</Label>
                  <Input
                    id="direccion_fiscal"
                    placeholder="Ej: AV. Industrial 1250"
                    value={formData.direccion_fiscal}
                    onChange={(e) => setFormData(prev => ({ ...prev, direccion_fiscal: e.target.value }))}
                    required
                  />
                </div>
                
                {/* Campo "anulado" solo visible en modo edición */}
                {editingProveedorId !== null && (
                    <div className="flex items-center justify-between p-3 border rounded-md">
                        <div className="space-y-1">
                            <Label htmlFor="anulado" className="text-base">
                                Estado del Proveedor
                            </Label>
                            <p className="text-sm text-muted-foreground">
                                {formData.anulado ? "El proveedor está Anulado (Inactivo)." : "El proveedor está Activo."}
                            </p>
                        </div>
                        <Switch
                            id="anulado"
                            checked={!formData.anulado} // Muestra ON para "No Anulado" (Activo)
                            onCheckedChange={(checked) => setFormData(prev => ({ ...prev, anulado: !checked }))} // Cambia anulado
                        />
                    </div>
                )}
                
                {/* Botones de acción */}
                <div className="flex justify-end space-x-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit">
                    {editingProveedorId ? "Actualizar Proveedor" : "Crear Proveedor"}
                  </Button>
                </div>
              </form>
            </DialogContent>
        </Dialog>
      </div>

      {/* Filtro de búsqueda */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nombre, RUC o email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
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
                  <TableHead>Empresa (Nombre)</TableHead>
                  <TableHead>Contacto</TableHead>
                  <TableHead>Dirección Fiscal</TableHead>
                  <TableHead>RUC / DNI</TableHead>
                  <TableHead>Registro</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedSuppliers.map((proveedor) => (
                  <TableRow key={proveedor.id_proveedor}>
                    <TableCell className="font-medium">{proveedor.nombre}</TableCell>
                    
                    <TableCell>
                      <div className="text-sm text-muted-foreground flex items-center mb-1">
                        <Mail className="h-3 w-3 mr-1" />
                        {proveedor.email_contacto}
                      </div>
                      <div className="text-sm text-muted-foreground flex items-center">
                        <Phone className="h-3 w-3 mr-1" />
                        {proveedor.numero_contacto}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                        <div className="text-sm text-muted-foreground flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {proveedor.direccion_fiscal}
                        </div>
                    </TableCell>
                    
                    <TableCell className="font-medium">{proveedor.ruc_dni}</TableCell>
                    
                    <TableCell>
                        <div className="text-sm text-muted-foreground flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatDate(proveedor.fecha_registro)}
                        </div>
                    </TableCell>

                    <TableCell>
                        {/* Estado basado en 'anulado' */}
                        {proveedor.anulado ? (
                            <Badge className="bg-red-100 text-red-800 hover:bg-red-200">
                                <XCircle className="h-3 w-3 mr-1" />
                                Anulado
                            </Badge>
                        ) : (
                            <Badge className="bg-green-100 text-green-800 hover:bg-green-200">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Activo
                            </Badge>
                        )}
                    </TableCell>
                    
                    <TableCell>
                      {canEditProveedores && (
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(proveedor)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(proveedor.id_proveedor)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
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
      
    </div>
  );
}