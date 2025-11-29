import { useState, useEffect } from "react";
import { Plus, Search, Edit, Shield, Mail, Activity, X, Loader2, CheckCircle, Clock, Ban, UserCheck } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "../context/AuthContext";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Checkbox } from "./ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { UserSessionModal } from "./UserSessionModal";
import { API_BASE_URL } from "../constants";
import { toast } from "sonner";

interface Permission {
  id_permiso: number;
  modulo: string;
  accion: string;
  descripcion_permiso: string;
}

interface Role {
  id_rol: number;
  nombre_rol: string;
  descripcion: string;
  anulado: boolean;
  fecha_creacion: string;
}

interface User {
  id_user: number;
  nombre: string;
  apellidos: string;
  email: string;
  ultimo_acceso: string | null;
  fecha_registro: string;
  anulado: boolean;
  roles: Role[];
  personal?: {
    id_personal: number;
    nombre_completo: string;
    direccion: string;
    referencia: string;
    dni: string;
    area: string;
    salario: number;
  };
}

interface PersonalData {
  nombre_completo: string;
  direccion: string;
  referencia: string;
  dni: string;
  area: string;
  salario: number;
}

const AREAS_PERSONAL = [
  { value: "PRODUCCION", label: "Producción" },
  { value: "ALMACEN", label: "Almacén" },
  { value: "VENTAS", label: "Ventas" },
  { value: "ADMINISTRACION", label: "Administración" },
  { value: "CALIDAD", label: "Calidad" },
  { value: "LOGISTICA", label: "Logística" },
  { value: "CONTABILIDAD", label: "Contabilidad" },
  { value: "RECURSOS_HUMANOS", label: "Recursos Humanos" },
];

export function UserManager() {
  const { canWrite } = useAuth();
  const canEditUsuarios = canWrite('USUARIOS');
  const canEditRoles = canWrite('ROLES');
  
  const [users, setUsers] = useState<User[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [isPermissionsModalOpen, setIsPermissionsModalOpen] = useState(false);
  const [selectedUserForPermissions, setSelectedUserForPermissions] = useState<User | null>(null);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);
  const [selectedUserForSessions, setSelectedUserForSessions] = useState("");
  const [userPermissions, setUserPermissions] = useState<number[]>([]);
  const [rolePermissions, setRolePermissions] = useState<number[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedUserRoles, setSelectedUserRoles] = useState<number[]>([]);

  const fetchUsers = async () => {
    try {
      const usersResponse = await fetch(`${API_BASE_URL}/v1/usuarios/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        if (usersData.success && usersData.data) setUsers(usersData.data);
      } else console.error('Error al cargar usuarios:', await usersResponse.text());
    } catch (error) { console.error('Error de conexión al cargar usuarios:', error); }
  };

  const fetchPermissions = async () => {
    try {
      const permissionsResponse = await fetch(`${API_BASE_URL}/v1/permisos`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (permissionsResponse.ok) {
        const permissionsData = await permissionsResponse.json();
        if (permissionsData.success && permissionsData.data) setPermissions(permissionsData.data);
      } else console.error('Error al cargar permisos:', await permissionsResponse.text());
    } catch (error) { console.error('Error de conexión al cargar permisos:', error); }
  };

  const fetchRoles = async () => {
    try {
      const rolesResponse = await fetch(`${API_BASE_URL}/v1/roles`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (rolesResponse.ok) {
        const rolesData = await rolesResponse.json();
        if (rolesData.success && rolesData.data) setRoles(rolesData.data);
      } else console.error('Error al cargar roles:', await rolesResponse.text());
    } catch (error) { console.error('Error de conexión al cargar roles:', error); }
  };

  useEffect(() => {
    fetchUsers();
    fetchPermissions();
    fetchRoles();
  }, []);

  const [userFormData, setUserFormData] = useState<Partial<User & { password?: string }>>({});
  const [personalFormData, setPersonalFormData] = useState<Partial<PersonalData>>({
    nombre_completo: '',
    direccion: '',
    referencia: '',
    dni: '',
    area: 'PRODUCCION',
    salario: 0
  });
  const [roleFormData, setRoleFormData] = useState<Partial<Omit<Role, 'id_rol' | 'fecha_creacion' | 'anulado'>>>({ nombre_rol: '', descripcion: '' });

  const filteredUsers = users.filter(user => {
    const fullName = `${user.nombre} ${user.apellidos}`.toLowerCase();
    return fullName.includes(searchTerm.toLowerCase()) || user.email.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const groupedPermissions = permissions.reduce((acc, permission) => {
    if (!acc[permission.modulo]) acc[permission.modulo] = [];
    acc[permission.modulo].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const url = editingUser ? `${API_BASE_URL}/v1/usuarios/${editingUser.id_user}` : `${API_BASE_URL}/v1/usuarios/`;
    const method = editingUser ? 'PUT' : 'POST';
    
    const body = editingUser ? {
      id_user: editingUser.id_user,
      nombre: userFormData.nombre,
      apellidos: userFormData.apellidos,
      email: userFormData.email,
      lista_roles: selectedUserRoles,
      personal: {
        nombre_completo: personalFormData.nombre_completo,
        direccion: personalFormData.direccion || "",
        referencia: personalFormData.referencia || "",
        dni: personalFormData.dni,
        area: personalFormData.area || "PRODUCCION",
        salario: personalFormData.salario || 0
      }
    } : {
      nombre: userFormData.nombre,
      apellidos: userFormData.apellidos,
      email: userFormData.email,
      password: userFormData.password,
      lista_roles: selectedUserRoles,
      personal: {
        nombre_completo: personalFormData.nombre_completo,
        direccion: personalFormData.direccion || "",
        referencia: personalFormData.referencia || "",
        dni: personalFormData.dni,
        area: personalFormData.area || "PRODUCCION",
        salario: personalFormData.salario || 0
      }
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        const result = await response.json();
        await fetchUsers();
        setIsUserDialogOpen(false);
        setEditingUser(null);
        setUserFormData({});
        setPersonalFormData({
          nombre_completo: '',
          direccion: '',
          referencia: '',
          dni: '',
          area: 'PRODUCCION',
          salario: 0
        });
        setSelectedUserRoles([]);
        
        // Mostrar notificación del estado del email (solo para nuevos usuarios)
        if (!editingUser && result.data?.email) {
          const emailInfo = result.data.email;
          if (emailInfo.enviado) {
            toast.success("Usuario creado exitosamente", {
              description: "Las credenciales fueron enviadas al correo del empleado.",
              icon: <CheckCircle className="h-4 w-4" />,
            });
          } else if (emailInfo.encolado) {
            toast.warning("Usuario creado - Email pendiente", {
              description: "El email está en cola y se enviará cuando haya conexión.",
              icon: <Clock className="h-4 w-4" />,
              duration: 6000,
            });
          } else {
            toast.info("Usuario creado", {
              description: "No se pudo enviar el email con las credenciales.",
            });
          }
        } else if (editingUser) {
          toast.success("Usuario actualizado exitosamente");
        }
      } else {
        const errorData = await response.json();
        toast.error("Error al guardar usuario", {
          description: errorData.data || errorData.message || "Ocurrió un error inesperado",
        });
      }
    } catch (error) { 
      console.error('Error de conexión al guardar usuario:', error);
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleUserStatus = async (user: User) => {
    const action = user.anulado ? 'reactivar' : 'anular';
    if (!confirm(`¿Estás seguro de ${action} al usuario ${user.nombre} ${user.apellidos}?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/v1/usuarios/${user.id_user}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        await fetchUsers();
        toast.success(`Usuario ${action === 'anular' ? 'anulado' : 'reactivado'} exitosamente`);
      } else {
        const errorData = await response.json();
        toast.error(`Error al ${action} usuario`, {
          description: errorData.data || errorData.message || "Ocurrió un error inesperado",
        });
      }
    } catch (error) {
      console.error(`Error al ${action} usuario:`, error);
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor",
      });
    }
  };

  const handleRoleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingRole ? `${API_BASE_URL}/v1/roles/${editingRole.id_rol}` : `${API_BASE_URL}/v1/roles/`;
    const method = editingRole ? 'PUT' : 'POST';
    
    const body = editingRole ? {
        id_rol: editingRole.id_rol,
        nombre_rol: roleFormData.nombre_rol,
        descripcion: roleFormData.descripcion,
        lista_permisos: rolePermissions
    } : {
        nombre_rol: roleFormData.nombre_rol,
        descripcion: roleFormData.descripcion,
        lista_permisos: rolePermissions
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok || data.success) {
        toast.success(editingRole ? 'Rol actualizado correctamente' : 'Rol creado correctamente');
        await fetchRoles();
        setIsRoleDialogOpen(false);
        setEditingRole(null);
        setRoleFormData({ nombre_rol: '', descripcion: '' });
        setRolePermissions([]);
      } else {
        toast.error(data.data || data.message || 'Error al guardar rol');
        console.error('Error al guardar rol:', data);
      }
    } catch (error) { 
      toast.error('Error de conexión al guardar rol');
      console.error('Error de conexión al guardar rol:', error); 
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormData(user);
    // Cargar los roles actuales del usuario
    setSelectedUserRoles(user.roles?.map(r => r.id_rol) || []);
    // Cargar datos de personal si existen
    if (user.personal) {
      setPersonalFormData({
        nombre_completo: user.personal.nombre_completo || '',
        direccion: user.personal.direccion || '',
        referencia: user.personal.referencia || '',
        dni: user.personal.dni || '',
        area: user.personal.area || 'PRODUCCION',
        salario: user.personal.salario || 0
      });
    }
    setIsUserDialogOpen(true);
  };

  const handleEditRole = async (role: Role) => {
    setEditingRole(role);
    setRoleFormData({ nombre_rol: role.nombre_rol, descripcion: role.descripcion });
    setIsRoleDialogOpen(true);
  
    // Fetch and set permissions for the role
    try {
      const response = await fetch(`${API_BASE_URL}/v1/roles/${role.id_rol}`);
      if (response.ok) {
        const roleData = await response.json();
        if (roleData.success && roleData.data && roleData.data.permisos) {
          setRolePermissions(roleData.data.permisos.map((p: any) => p.id_permiso));
        } else {
          setRolePermissions([]);
        }
      } else {
        console.error('Error al cargar los permisos del rol:', await response.text());
        setRolePermissions([]);
      }
    } catch (error) {
      console.error('Error de conexión al cargar los permisos del rol:', error);
      setRolePermissions([]);
    }
  };

  const openAddUserDialog = () => {
    setEditingUser(null);
    setUserFormData({});
    setPersonalFormData({
      nombre_completo: '',
      direccion: '',
      referencia: '',
      dni: '',
      area: 'PRODUCCION',
      salario: 0
    });
    setSelectedUserRoles([]);
    setIsUserDialogOpen(true);
  };

  const openAddRoleDialog = () => {
    setEditingRole(null);
    setRoleFormData({ nombre_rol: '', descripcion: '' });
    setRolePermissions([]);
    setIsRoleDialogOpen(true);
  };

  const handleManagePermissions = async (user: User) => {
    setSelectedUserForPermissions(user);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/usuario-permisos/${user.id_user}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        setUserPermissions(data.success && data.data ? data.data.map((p: any) => p.id_permiso) : []);
      } else {
        console.error('Error al cargar permisos del usuario:', await response.text());
        setUserPermissions([]);
      }
    } catch (error) {
      console.error('Error de conexión al cargar permisos del usuario:', error);
      setUserPermissions([]);
    }
    setIsPermissionsModalOpen(true);
  };

  const handleSaveUserPermissions = async () => {
    if (!selectedUserForPermissions) return;
    try {
      const response = await fetch(`${API_BASE_URL}/v1/usuario-permisos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_user: selectedUserForPermissions.id_user,
          permisos: userPermissions
        })
      });
      if (response.ok) {
        console.log('Permisos actualizados correctamente');
        setIsPermissionsModalOpen(false);
        setSelectedUserForPermissions(null);
        setUserPermissions([]);
      } else console.error('Error al guardar permisos:', await response.text());
    } catch (error) { console.error('Error de conexión al guardar permisos:', error); }
  };

  const handleUserPermissionToggle = (permissionId: number, checked: boolean) => {
    setUserPermissions(prev => checked ? [...prev, permissionId] : prev.filter(id => id !== permissionId));
  };

  const handleRolePermissionToggle = (permissionId: number, checked: boolean) => {
    setRolePermissions(prev => checked ? [...prev, permissionId] : prev.filter(id => id !== permissionId));
  };

  const handleViewSessions = (userName: string) => {
    setSelectedUserForSessions(userName);
    setIsSessionModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gestión de Acceso</h2>
          <p className="text-muted-foreground">Administra usuarios, roles y permisos del sistema.</p>
        </div>
      </div>

      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">Permisos</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar usuarios por nombre o email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            {canEditUsuarios && (
              <Button onClick={openAddUserDialog}><Plus className="h-4 w-4 mr-2" />Nuevo Usuario</Button>
            )}
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Lista de Usuarios</CardTitle>
              <CardDescription>{filteredUsers.length} usuarios encontrados</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre Completo</TableHead>
                    <TableHead>Email</TableHead>
                      <TableHead>Roles</TableHead>
                    <TableHead>Área</TableHead>
                    <TableHead>Último Acceso</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.id_user}>
                      <TableCell><div className="font-medium">{user.nombre} {user.apellidos}</div></TableCell>
                      <TableCell><div className="flex items-center text-sm"><Mail className="h-3 w-3 mr-1.5" />{user.email}</div></TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {user.roles?.length > 0 ? user.roles.map(role => (
                            <Badge key={role.id_rol} variant="secondary" className="text-xs">{role.nombre_rol}</Badge>
                          )) : <span className="text-muted-foreground text-xs">Sin rol</span>}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{user.personal?.area ? AREAS_PERSONAL.find(a => a.value === user.personal?.area)?.label || user.personal?.area : '-'}</span>
                      </TableCell>
                      <TableCell>{user.ultimo_acceso ? new Date(user.ultimo_acceso).toLocaleDateString() : 'Nunca'}</TableCell>
                      <TableCell><Badge variant={user.anulado ? "destructive" : "outline"}>{user.anulado ? "Anulado" : "Activo"}</Badge></TableCell>
                      <TableCell className="text-right">
                        <div className="flex space-x-2 justify-end">
                          <Button variant="outline" size="icon" onClick={() => handleViewSessions(user.nombre)} title="Ver sesiones"><Activity className="h-4 w-4" /></Button>
                          {canEditUsuarios && (
                            <>
                              <Button variant="outline" size="icon" onClick={() => handleManagePermissions(user)} title="Gestionar permisos"><Shield className="h-4 w-4" /></Button>
                              <Button variant="outline" size="icon" onClick={() => handleEditUser(user)} title="Editar usuario"><Edit className="h-4 w-4" /></Button>
                              <Button 
                                variant={user.anulado ? "outline" : "destructive"} 
                                size="icon" 
                                onClick={() => handleToggleUserStatus(user)} 
                                title={user.anulado ? "Reactivar usuario" : "Anular usuario"}
                              >
                                {user.anulado ? <UserCheck className="h-4 w-4" /> : <Ban className="h-4 w-4" />}
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          <div className="flex justify-end">
            {canEditRoles && (
              <Button onClick={openAddRoleDialog}><Plus className="h-4 w-4 mr-2" />Nuevo Rol</Button>
            )}
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Lista de Roles</CardTitle>
              <CardDescription>{roles.length} roles definidos en el sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre del Rol</TableHead>
                    <TableHead>Descripción</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {roles.map((role) => (
                    <TableRow key={role.id_rol}>
                      <TableCell className="font-medium">{role.nombre_rol}</TableCell>
                      <TableCell>{role.descripcion}</TableCell>
                      <TableCell><Badge variant={role.anulado ? "destructive" : "outline"}>{role.anulado ? "Anulado" : "Activo"}</Badge></TableCell>
                      <TableCell className="text-right">
                        <div className="flex space-x-2 justify-end">
                          {canEditRoles && (
                            <>
                              <Button variant="outline" size="icon" title="Asignar permisos al rol (Próximamente)"><Shield className="h-4 w-4" /></Button>
                              <Button variant="outline" size="icon" onClick={() => handleEditRole(role)} title="Editar rol"><Edit className="h-4 w-4" /></Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Permisos del Sistema</CardTitle>
              <CardDescription>Estos son todos los permisos disponibles, agrupados por módulo.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
                <div key={module}>
                  <h4 className="font-semibold text-lg mb-3 border-b pb-2">{module}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {modulePermissions.map((permission) => (
                      <div key={permission.id_permiso} className="p-3 bg-muted/40 rounded-lg">
                        <div className="font-medium">{permission.accion}</div>
                        <div className="text-sm text-muted-foreground">{permission.descripcion_permiso}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingUser ? "Editar Usuario" : "Nuevo Usuario"}</DialogTitle>
            <DialogDescription>{editingUser ? "Modifica la información del usuario." : "Crea un nuevo usuario y empleado para el sistema."}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUserSubmit} className="space-y-4">
            {/* Sección: Datos de Acceso */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm text-muted-foreground border-b pb-2">Datos de Acceso</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nombre">Nombre</Label>
                  <Input id="nombre" placeholder="Ej: Ana" value={userFormData.nombre || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, nombre: e.target.value }))} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="apellidos">Apellidos</Label>
                  <Input id="apellidos" placeholder="Ej: García López" value={userFormData.apellidos || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, apellidos: e.target.value }))} required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Correo Electrónico</Label>
                  <Input id="email" type="email" placeholder="usuario@empresa.com" value={userFormData.email || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, email: e.target.value }))} required />
                </div>
                {!editingUser && (
                  <div className="space-y-2">
                    <Label htmlFor="password">Contraseña</Label>
                    <Input id="password" type="password" placeholder="Contraseña segura" value={userFormData.password || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, password: e.target.value }))} required />
                  </div>
                )}
              </div>
            </div>

            {/* Sección: Datos del Empleado */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm text-muted-foreground border-b pb-2">Datos del Empleado</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nombre_completo">Nombre Completo</Label>
                  <Input id="nombre_completo" placeholder="Ej: Ana María García López" value={personalFormData.nombre_completo || ""} onChange={(e) => setPersonalFormData(prev => ({ ...prev, nombre_completo: e.target.value }))} required={!editingUser} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dni">DNI</Label>
                  <Input id="dni" placeholder="Ej: 12345678" value={personalFormData.dni || ""} onChange={(e) => setPersonalFormData(prev => ({ ...prev, dni: e.target.value }))} required={!editingUser} maxLength={8} disabled={!!editingUser} />
                  {editingUser && <p className="text-xs text-muted-foreground">El DNI no se puede modificar</p>}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="area">Área</Label>
                  <Select value={personalFormData.area || "PRODUCCION"} onValueChange={(value: string) => setPersonalFormData(prev => ({ ...prev, area: value }))}>
                    <SelectTrigger id="area">
                      <SelectValue placeholder="Selecciona área" />
                    </SelectTrigger>
                    <SelectContent>
                      {AREAS_PERSONAL.map((area) => (
                        <SelectItem key={area.value} value={area.value}>{area.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salario">Salario (S/.)</Label>
                  <Input id="salario" type="number" placeholder="0.00" min="0" step="0.01" value={personalFormData.salario || ""} onChange={(e) => setPersonalFormData(prev => ({ ...prev, salario: parseFloat(e.target.value) || 0 }))} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="direccion">Dirección</Label>
                <Input id="direccion" placeholder="Ej: Av. Principal 123, Lima" value={personalFormData.direccion || ""} onChange={(e) => setPersonalFormData(prev => ({ ...prev, direccion: e.target.value }))} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="referencia">Referencia</Label>
                <Input id="referencia" placeholder="Ej: Frente al parque central" value={personalFormData.referencia || ""} onChange={(e) => setPersonalFormData(prev => ({ ...prev, referencia: e.target.value }))} />
              </div>
            </div>

            {/* Sección: Asignación de Roles */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm text-muted-foreground border-b pb-2">Roles del Usuario</h4>
              <div className="space-y-2">
                <Label>Selecciona los roles</Label>
                <div className="grid grid-cols-2 gap-2 p-3 border rounded-md max-h-[200px] overflow-y-auto">
                  {roles.filter(r => !r.anulado).map((role) => (
                    <div key={role.id_rol} className="flex items-center space-x-2">
                      <Checkbox
                        id={`user-role-${role.id_rol}`}
                        checked={selectedUserRoles.includes(role.id_rol)}
                        onCheckedChange={(checked: boolean | 'indeterminate') => {
                          if (checked) {
                            setSelectedUserRoles(prev => [...prev, role.id_rol]);
                          } else {
                            setSelectedUserRoles(prev => prev.filter(id => id !== role.id_rol));
                          }
                        }}
                      />
                      <Label htmlFor={`user-role-${role.id_rol}`} className="text-sm font-normal cursor-pointer">
                        <div className="font-medium">{role.nombre_rol}</div>
                        {role.descripcion && <div className="text-xs text-muted-foreground">{role.descripcion}</div>}
                      </Label>
                    </div>
                  ))}
                  {roles.filter(r => !r.anulado).length === 0 && (
                    <span className="text-sm text-muted-foreground col-span-2">No hay roles disponibles. Crea uno primero.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsUserDialogOpen(false)} disabled={isSubmitting}>Cancelar</Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {editingUser ? "Actualizando..." : "Creando..."}
                  </>
                ) : (
                  editingUser ? "Actualizar" : "Crear Usuario"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
        {/* CORRECCIÓN 1: Ancho fijo (sm:max-w-lg) y manejo de altura máxima */}
        <DialogContent className="sm:max-w-lg w-full max-h-[90vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>{editingRole ? "Editar Rol" : "Nuevo Rol"}</DialogTitle>
            <DialogDescription>{editingRole ? "Modifica la información del rol." : "Crea un nuevo rol para asignar a los usuarios."}</DialogDescription>
          </DialogHeader>
          
          {/* Agregamos overflow-y-auto al form para que scrollee si la pantalla es pequeña */}
          <form onSubmit={handleRoleSubmit} className="space-y-4 overflow-y-auto p-1">
            <div className="space-y-2">
              <Label htmlFor="nombre_rol">Nombre del Rol</Label>
              <Input id="nombre_rol" placeholder="Ej: Gerente de Producción" value={roleFormData.nombre_rol || ""} onChange={(e) => setRoleFormData(prev => ({ ...prev, nombre_rol: e.target.value }))} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="descripcion_rol">Descripción</Label>
              <Input id="descripcion_rol" placeholder="Ej: Responsable de la línea de producción" value={roleFormData.descripcion || ""} onChange={(e) => setRoleFormData(prev => ({ ...prev, descripcion: e.target.value }))} required />
            </div>
            
            {/* Permisos agrupados por módulo */}
            <div className="space-y-3">
              <Label>Permisos del Rol</Label>
              <div className="border rounded-md p-3 max-h-[300px] overflow-y-auto space-y-4">
                {Object.entries(
                  permissions.reduce((acc, permission) => {
                    if (!acc[permission.modulo]) acc[permission.modulo] = [];
                    acc[permission.modulo].push(permission);
                    return acc;
                  }, {} as Record<string, Permission[]>)
                ).map(([modulo, modulePermissions]) => (
                  <div key={modulo} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h5 className="font-medium text-sm text-primary uppercase tracking-wide">{modulo}</h5>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-6 text-xs"
                        onClick={() => {
                          const moduleIds = modulePermissions.map(p => p.id_permiso);
                          const allSelected = moduleIds.every(id => rolePermissions.includes(id));
                          if (allSelected) {
                            setRolePermissions(prev => prev.filter(id => !moduleIds.includes(id)));
                          } else {
                            setRolePermissions(prev => [...new Set([...prev, ...moduleIds])]);
                          }
                        }}
                      >
                        {modulePermissions.every(p => rolePermissions.includes(p.id_permiso)) ? "Deseleccionar todo" : "Seleccionar todo"}
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 gap-2 pl-2">
                      {modulePermissions.map((permission) => (
                        <div key={permission.id_permiso} className="flex items-start space-x-2">
                          <Checkbox
                            id={`role-perm-${permission.id_permiso}`}
                            checked={rolePermissions.includes(permission.id_permiso)}
                            onCheckedChange={(checked: boolean | 'indeterminate') => {
                              if (checked) {
                                setRolePermissions(prev => [...prev, permission.id_permiso]);
                              } else {
                                setRolePermissions(prev => prev.filter(id => id !== permission.id_permiso));
                              }
                            }}
                          />
                          <Label htmlFor={`role-perm-${permission.id_permiso}`} className="text-sm font-normal cursor-pointer leading-tight">
                            <span className="font-medium">{permission.accion}</span>
                            {permission.descripcion_permiso && (
                              <span className="block text-xs text-muted-foreground">{permission.descripcion_permiso}</span>
                            )}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                {permissions.length === 0 && (
                  <span className="text-sm text-muted-foreground">No hay permisos disponibles</span>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsRoleDialogOpen(false)}>Cancelar</Button>
              <Button type="submit">{editingRole ? "Actualizar Rol" : "Crear Rol"}</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <UserSessionModal isOpen={isSessionModalOpen} onClose={() => setIsSessionModalOpen(false)} username={selectedUserForSessions} />

      <Dialog open={isPermissionsModalOpen} onOpenChange={setIsPermissionsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Gestionar Permisos - {selectedUserForPermissions?.nombre} {selectedUserForPermissions?.apellidos}</DialogTitle>
            <DialogDescription>Selecciona los permisos individuales que tendrá este usuario.</DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
              <div key={module} className="space-y-3">
                <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">{module}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {modulePermissions.map((permission) => (
                    <div key={permission.id_permiso} className="flex items-center space-x-2">
                      <Checkbox
                        id={`permission-${permission.id_permiso}`}
                        checked={userPermissions.includes(permission.id_permiso)}
                        onCheckedChange={(checked: boolean | 'indeterminate') => handleUserPermissionToggle(permission.id_permiso, checked as boolean)}
                      />
                      <Label htmlFor={`permission-${permission.id_permiso}`} className="text-sm font-normal cursor-pointer">
                        <div className="font-medium">{permission.accion}</div>
                        <div className="text-xs text-muted-foreground">{permission.descripcion_permiso}</div>
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsPermissionsModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleSaveUserPermissions}>Guardar Permisos</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}