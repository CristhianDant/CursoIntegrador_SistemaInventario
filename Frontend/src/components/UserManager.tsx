import { useState, useEffect } from "react";
import { Plus, Search, Edit, Trash2, User, Shield, Mail, Phone, UserCheck, Monitor, Activity } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Switch } from "./ui/switch";
import { Checkbox } from "./ui/checkbox";
import { DeviceManager } from "./DeviceManager";
import { UserSessionModal } from "./UserSessionModal";
import { API_BASE_URL } from "../constants";

interface Permission {
  id_permiso: number;
  modulo: string;
  accion: string;
  descripcion_permiso: string;
}

interface Role {
  id: number;
  name: string;
  description: string;
  permissions: string[];
  isActive: boolean;
  createdDate: string;
}

interface User {
  id_user: number;
  nombre: string;
  apellidos: string;
  email: string;
  es_admin: boolean;
  ultimo_acceso: string | null;
  fecha_registro: string;
  anulado: boolean;
}

// Permisos disponibles en el sistema (se cargarán desde API)
const mockPermissions: Permission[] = [];

// Roles predefinidos
const mockRoles: Role[] = [
  {
    id: 1,
    name: 'Administrador',
    description: 'Acceso completo al sistema',
    permissions: [],
    isActive: true,
    createdDate: '2024-01-15'
  },
  {
    id: 2,
    name: 'Gerente',
    description: 'Gestión general sin administración de usuarios',
    permissions: [],
    isActive: true,
    createdDate: '2024-01-20'
  },
  {
    id: 3,
    name: 'Operador de Producción',
    description: 'Manejo de inventario y producción',
    permissions: [],
    isActive: true,
    createdDate: '2024-02-01'
  },
  {
    id: 4,
    name: 'Vendedor',
    description: 'Registro de ventas y consulta básica',
    permissions: [],
    isActive: true,
    createdDate: '2024-02-10'
  }
];

// Usuarios de ejemplo (vacío, se cargará desde API)
const mockUsers: User[] = [];

export function UserManager() {
  const [users, setUsers] = useState<User[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roles, setRoles] = useState<Role[]>(mockRoles);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRole, setSelectedRole] = useState("all");
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [isPermissionsModalOpen, setIsPermissionsModalOpen] = useState(false);
  const [selectedUserForPermissions, setSelectedUserForPermissions] = useState<User | null>(null);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);
  const [selectedUserForSessions, setSelectedUserForSessions] = useState("");
  const [userPermissions, setUserPermissions] = useState<number[]>([]);

  // Cargar usuarios y permisos desde API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Cargar usuarios
        const usersResponse = await fetch(`${API_BASE_URL}/v1/usuarios/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // TODO: Agregar JWT token cuando esté disponible
            //'Authorization': `Bearer ${token}`
          }
        });

        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          if (usersData.success && usersData.data) {
            setUsers(usersData.data);
          }
        } else {
          console.error('Error al cargar usuarios:', await usersResponse.text());
        }

        // Cargar permisos
        const permissionsResponse = await fetch(`${API_BASE_URL}/v1/permisos`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // TODO: Agregar JWT token cuando esté disponible
            //'Authorization': `Bearer ${token}`
          }
        });

        if (permissionsResponse.ok) {
          const permissionsData = await permissionsResponse.json();
          if (permissionsData.success && permissionsData.data) {
            setPermissions(permissionsData.data);
          }
        } else {
          console.error('Error al cargar permisos:', await permissionsResponse.text());
        }
      } catch (error) {
        console.error('Error de conexión:', error);
      }
    };

    fetchData();
  }, []);
  const [userFormData, setUserFormData] = useState<Partial<User & { password?: string }>>({});
  const [roleFormData, setRoleFormData] = useState<Partial<Role>>({ permissions: [] });

  const filteredUsers = users.filter(user => {
    const fullName = `${user.nombre} ${user.apellidos}`.toLowerCase();
    const matchesSearch = fullName.includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const groupedPermissions = permissions.reduce((acc, permission) => {
    if (!acc[permission.modulo]) {
      acc[permission.modulo] = [];
    }
    acc[permission.modulo].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  // Manejar usuarios
  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_BASE_URL}/v1/usuarios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Agregar JWT token cuando esté disponible
          //'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: userFormData.nombre,
          apellidos: userFormData.apellidos,
          email: userFormData.email,
          password: userFormData.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Recargar usuarios
        const usersResponse = await fetch(`${API_BASE_URL}/v1/usuarios/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // TODO: Agregar JWT token cuando esté disponible
            //'Authorization': `Bearer ${token}`
          }
        });
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          if (usersData.success && usersData.data) {
            setUsers(usersData.data);
          }
        }
        setIsUserDialogOpen(false);
        setEditingUser(null);
        setUserFormData({});
      } else {
        console.error('Error al crear usuario:', await response.text());
      }
    } catch (error) {
      console.error('Error de conexión al crear usuario:', error);
    }
  };

  // Manejar roles
  const handleRoleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingRole) {
      setRoles(prev => 
        prev.map(role => 
          role.id === editingRole.id 
            ? { ...role, ...roleFormData } as Role
            : role
        )
      );
      
      // Actualizar permisos de usuarios con este rol
      setUsers(prev =>
        prev.map(user =>
          user.roleId === editingRole.id
            ? { ...user, permissions: roleFormData.permissions || [] }
            : user
        )
      );
    } else {
      const newRole: Role = {
        id: Math.max(...roles.map(r => r.id)) + 1,
        ...roleFormData,
        isActive: true,
        createdDate: new Date().toISOString().split('T')[0]
      } as Role;
      setRoles(prev => [...prev, newRole]);
    }
    
    setIsRoleDialogOpen(false);
    setEditingRole(null);
    setRoleFormData({ permissions: [] });
  };

  const toggleUserStatus = (id_user: number) => {
    setUsers(prev =>
      prev.map(user =>
        user.id_user === id_user ? { ...user, anulado: !user.anulado } : user
      )
    );
  };

  const toggleRoleStatus = (id: number) => {
    setRoles(prev =>
      prev.map(role =>
        role.id === id ? { ...role, isActive: !role.isActive } : role
      )
    );
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormData(user);
    setIsUserDialogOpen(true);
  };

  const handleEditRole = (role: Role) => {
    setEditingRole(role);
    setRoleFormData(role);
    setIsRoleDialogOpen(true);
  };

  const openAddUserDialog = () => {
    setEditingUser(null);
    setUserFormData({});
    setIsUserDialogOpen(true);
  };

  const openAddRoleDialog = () => {
    setEditingRole(null);
    setRoleFormData({ permissions: [] });
    setIsRoleDialogOpen(true);
  };

  const handlePermissionToggle = (permissionId: string, checked: boolean) => {
    setRoleFormData(prev => ({
      ...prev,
      permissions: checked
        ? [...(prev.permissions || []), permissionId]
        : (prev.permissions || []).filter(p => p !== permissionId)
    }));
  };

  const handleManagePermissions = async (user: User) => {
    setSelectedUserForPermissions(user);
    
    try {
      // Cargar permisos actuales del usuario
      const response = await fetch(`${API_BASE_URL}/v1/usuario-permisos/${user.id_user}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Agregar JWT token cuando esté disponible
          //'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setUserPermissions(data.data.map((p: any) => p.id_permiso));
        } else {
          setUserPermissions([]);
        }
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
        headers: {
          'Content-Type': 'application/json',
          // TODO: Agregar JWT token cuando esté disponible
          //'Authorization': `Bearer ${token}`
        },
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
      } else {
        console.error('Error al guardar permisos:', await response.text());
      }
    } catch (error) {
      console.error('Error de conexión al guardar permisos:', error);
    }
  };

  const handleUserPermissionToggle = (permissionId: number, checked: boolean) => {
    setUserPermissions(prev => 
      checked 
        ? [...prev, permissionId]
        : prev.filter(id => id !== permissionId)
    );
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <Badge className="bg-green-100 text-green-800">Activo</Badge>
    ) : (
      <Badge className="bg-red-100 text-red-800">Inactivo</Badge>
    );
  };

  const handleViewSessions = (userName: string) => {
    setSelectedUserForSessions(userName);
    setIsSessionModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Usuarios y Permisos</h2>
          <p className="text-muted-foreground">Administra usuarios y permisos del sistema</p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
        </TabsList>

        {/* Tab de Usuarios */}
        <TabsContent value="users" className="space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar usuarios..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Button onClick={openAddUserDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Usuario
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Lista de Usuarios</CardTitle>
              <CardDescription>
                {filteredUsers.length} usuarios encontrados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nombre</TableHead>
                      <TableHead>Apellidos</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Admin</TableHead>
                      <TableHead>Último Acceso</TableHead>
                      <TableHead>Anulado</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id_user}>
                        <TableCell>
                          <div className="font-medium">{user.nombre}</div>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">{user.apellidos}</div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center text-sm">
                            <Mail className="h-3 w-3 mr-1" />
                            {user.email}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.es_admin ? "default" : "secondary"}>
                            {user.es_admin ? "Sí" : "No"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {user.ultimo_acceso ? new Date(user.ultimo_acceso).toLocaleDateString() : 'Nunca'}
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.anulado ? "destructive" : "outline"}>
                            {user.anulado ? "Anulado" : "Activo"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewSessions(user.nombre)}
                              title="Ver sesiones"
                            >
                              <Activity className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleManagePermissions(user)}
                              title="Gestionar permisos"
                            >
                              <Shield className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditUser(user)}
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            {user.id_user !== 1 && ( // No permitir eliminar admin principal
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialog para Usuario */}
      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingUser ? "Editar Usuario" : "Nuevo Usuario"}
            </DialogTitle>
            <DialogDescription>
              {editingUser ? "Modifica la información del usuario" : "Crea un nuevo usuario del sistema"}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleUserSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nombre">Nombre</Label>
              <Input
                id="nombre"
                placeholder="Ej: Ana"
                value={userFormData.nombre || ""}
                onChange={(e) => setUserFormData(prev => ({ ...prev, nombre: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="apellidos">Apellidos</Label>
              <Input
                id="apellidos"
                placeholder="Ej: García"
                value={userFormData.apellidos || ""}
                onChange={(e) => setUserFormData(prev => ({ ...prev, apellidos: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico</Label>
              <Input
                id="email"
                type="email"
                placeholder="usuario@sweetstock.com"
                value={userFormData.email || ""}
                onChange={(e) => setUserFormData(prev => ({ ...prev, email: e.target.value }))}
                required
              />
            </div>

            {!editingUser && (
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Contraseña segura"
                  value={userFormData.password || ""}
                  onChange={(e) => setUserFormData(prev => ({ ...prev, password: e.target.value }))}
                  required
                />
              </div>
            )}
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsUserDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingUser ? "Actualizar" : "Crear Usuario"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Sesiones de Usuario */}
      <UserSessionModal
        isOpen={isSessionModalOpen}
        onClose={() => setIsSessionModalOpen(false)}
        username={selectedUserForSessions}
      />

      {/* Modal de Permisos de Usuario */}
      <Dialog open={isPermissionsModalOpen} onOpenChange={setIsPermissionsModalOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Gestionar Permisos - {selectedUserForPermissions?.nombre} {selectedUserForPermissions?.apellidos}
            </DialogTitle>
            <DialogDescription>
              Selecciona los permisos que tendrá este usuario en el sistema
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
              <div key={module} className="space-y-3">
                <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
                  {module}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {modulePermissions.map((permission) => (
                    <div key={permission.id_permiso} className="flex items-center space-x-2">
                      <Checkbox
                        id={`permission-${permission.id_permiso}`}
                        checked={userPermissions.includes(permission.id_permiso)}
                        onCheckedChange={(checked) => 
                          handleUserPermissionToggle(permission.id_permiso, checked as boolean)
                        }
                      />
                      <Label 
                        htmlFor={`permission-${permission.id_permiso}`}
                        className="text-sm font-normal cursor-pointer"
                      >
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
            <Button type="button" variant="outline" onClick={() => setIsPermissionsModalOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveUserPermissions}>
              Guardar Permisos
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}