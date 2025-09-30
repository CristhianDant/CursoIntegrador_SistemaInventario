import { useState } from "react";
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

interface Permission {
  id: string;
  name: string;
  description: string;
  module: string;
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
  id: number;
  name: string;
  email: string;
  phone: string;
  roleId: number;
  roleName: string;
  isActive: boolean;
  lastLogin: string;
  createdDate: string;
  permissions: string[];
}

// Permisos disponibles en el sistema
const systemPermissions: Permission[] = [
  // Dashboard
  { id: 'dashboard_view', name: 'Ver Dashboard', description: 'Acceso al panel principal', module: 'Dashboard' },
  
  // Inventario
  { id: 'inventory_view', name: 'Ver Inventario', description: 'Consultar inventario de insumos', module: 'Inventario' },
  { id: 'inventory_create', name: 'Crear Insumos', description: 'Agregar nuevos insumos', module: 'Inventario' },
  { id: 'inventory_edit', name: 'Editar Insumos', description: 'Modificar insumos existentes', module: 'Inventario' },
  { id: 'inventory_delete', name: 'Eliminar Insumos', description: 'Eliminar insumos del sistema', module: 'Inventario' },
  
  // Recetas
  { id: 'recipes_view', name: 'Ver Recetas', description: 'Consultar recetas', module: 'Recetas' },
  { id: 'recipes_create', name: 'Crear Recetas', description: 'Agregar nuevas recetas', module: 'Recetas' },
  { id: 'recipes_edit', name: 'Editar Recetas', description: 'Modificar recetas existentes', module: 'Recetas' },
  { id: 'recipes_delete', name: 'Eliminar Recetas', description: 'Eliminar recetas del sistema', module: 'Recetas' },
  
  // Productos
  { id: 'products_view', name: 'Ver Productos', description: 'Consultar productos terminados', module: 'Productos' },
  { id: 'products_create', name: 'Crear Productos', description: 'Registrar nuevos productos', module: 'Productos' },
  { id: 'products_edit', name: 'Editar Productos', description: 'Modificar productos existentes', module: 'Productos' },
  { id: 'products_production', name: 'Registrar Producción', description: 'Registrar producciones', module: 'Productos' },
  { id: 'products_sales', name: 'Registrar Ventas', description: 'Registrar ventas de productos', module: 'Productos' },
  
  // Alertas
  { id: 'alerts_view', name: 'Ver Alertas', description: 'Acceso al centro de alertas', module: 'Alertas' },
  { id: 'alerts_manage', name: 'Gestionar Alertas', description: 'Descartar y gestionar alertas', module: 'Alertas' },
  
  // Reportes
  { id: 'reports_view', name: 'Ver Reportes', description: 'Acceso a reportes básicos', module: 'Reportes' },
  { id: 'reports_advanced', name: 'Reportes Avanzados', description: 'Acceso a todos los reportes', module: 'Reportes' },
  { id: 'reports_export', name: 'Exportar Reportes', description: 'Exportar reportes a archivos', module: 'Reportes' },
  
  // Usuarios (solo admin)
  { id: 'users_view', name: 'Ver Usuarios', description: 'Consultar usuarios del sistema', module: 'Usuarios' },
  { id: 'users_create', name: 'Crear Usuarios', description: 'Agregar nuevos usuarios', module: 'Usuarios' },
  { id: 'users_edit', name: 'Editar Usuarios', description: 'Modificar usuarios existentes', module: 'Usuarios' },
  { id: 'users_delete', name: 'Eliminar Usuarios', description: 'Eliminar usuarios del sistema', module: 'Usuarios' },
  { id: 'roles_manage', name: 'Gestionar Roles', description: 'Crear y modificar roles', module: 'Usuarios' },
  
  // Configuración
  { id: 'settings_view', name: 'Ver Configuración', description: 'Acceso a configuración básica', module: 'Configuración' },
  { id: 'settings_edit', name: 'Editar Configuración', description: 'Modificar configuración del sistema', module: 'Configuración' },
];

// Roles predefinidos
const mockRoles: Role[] = [
  {
    id: 1,
    name: 'Administrador',
    description: 'Acceso completo al sistema',
    permissions: systemPermissions.map(p => p.id),
    isActive: true,
    createdDate: '2024-01-15'
  },
  {
    id: 2,
    name: 'Gerente',
    description: 'Gestión general sin administración de usuarios',
    permissions: [
      'dashboard_view', 'inventory_view', 'inventory_create', 'inventory_edit',
      'recipes_view', 'recipes_create', 'recipes_edit',
      'products_view', 'products_create', 'products_edit', 'products_production', 'products_sales',
      'alerts_view', 'alerts_manage',
      'reports_view', 'reports_advanced', 'reports_export',
      'settings_view'
    ],
    isActive: true,
    createdDate: '2024-01-20'
  },
  {
    id: 3,
    name: 'Operador de Producción',
    description: 'Manejo de inventario y producción',
    permissions: [
      'dashboard_view',
      'inventory_view', 'inventory_edit',
      'recipes_view',
      'products_view', 'products_production',
      'alerts_view'
    ],
    isActive: true,
    createdDate: '2024-02-01'
  },
  {
    id: 4,
    name: 'Vendedor',
    description: 'Registro de ventas y consulta básica',
    permissions: [
      'dashboard_view',
      'inventory_view',
      'products_view', 'products_sales',
      'alerts_view'
    ],
    isActive: true,
    createdDate: '2024-02-10'
  }
];

// Usuarios de ejemplo
const mockUsers: User[] = [
  {
    id: 1,
    name: 'Admin Principal',
    email: 'admin@sweetstock.com',
    phone: '+1234567890',
    roleId: 1,
    roleName: 'Administrador',
    isActive: true,
    lastLogin: '2024-09-03',
    createdDate: '2024-01-15',
    permissions: systemPermissions.map(p => p.id)
  },
  {
    id: 2,
    name: 'María González',
    email: 'maria.gonzalez@sweetstock.com',
    phone: '+1234567891',
    roleId: 2,
    roleName: 'Gerente',
    isActive: true,
    lastLogin: '2024-09-02',
    createdDate: '2024-02-01',
    permissions: mockRoles.find(r => r.id === 2)?.permissions || []
  },
  {
    id: 3,
    name: 'Carlos Rodríguez',
    email: 'carlos.rodriguez@sweetstock.com',
    phone: '+1234567892',
    roleId: 3,
    roleName: 'Operador de Producción',
    isActive: true,
    lastLogin: '2024-09-01',
    createdDate: '2024-02-15',
    permissions: mockRoles.find(r => r.id === 3)?.permissions || []
  },
  {
    id: 4,
    name: 'Ana Martínez',
    email: 'ana.martinez@sweetstock.com',
    phone: '+1234567893',
    roleId: 4,
    roleName: 'Vendedor',
    isActive: false,
    lastLogin: '2024-08-28',
    createdDate: '2024-03-01',
    permissions: mockRoles.find(r => r.id === 4)?.permissions || []
  }
];

export function UserManager() {
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [roles, setRoles] = useState<Role[]>(mockRoles);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRole, setSelectedRole] = useState("all");
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [userFormData, setUserFormData] = useState<Partial<User>>({});
  const [roleFormData, setRoleFormData] = useState<Partial<Role>>({ permissions: [] });
  const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);
  const [selectedUserForSessions, setSelectedUserForSessions] = useState<string>("");

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === "all" || user.roleId.toString() === selectedRole;
    return matchesSearch && matchesRole;
  });

  const groupedPermissions = systemPermissions.reduce((acc, permission) => {
    if (!acc[permission.module]) {
      acc[permission.module] = [];
    }
    acc[permission.module].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  // Manejar usuarios
  const handleUserSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const selectedRole = roles.find(r => r.id === userFormData.roleId);
    
    if (editingUser) {
      setUsers(prev => 
        prev.map(user => 
          user.id === editingUser.id 
            ? { 
                ...user, 
                ...userFormData,
                roleName: selectedRole?.name || user.roleName,
                permissions: selectedRole?.permissions || user.permissions
              } as User
            : user
        )
      );
    } else {
      const newUser: User = {
        id: Math.max(...users.map(u => u.id)) + 1,
        ...userFormData,
        roleName: selectedRole?.name || "",
        permissions: selectedRole?.permissions || [],
        isActive: true,
        lastLogin: '',
        createdDate: new Date().toISOString().split('T')[0]
      } as User;
      setUsers(prev => [...prev, newUser]);
    }
    
    setIsUserDialogOpen(false);
    setEditingUser(null);
    setUserFormData({});
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

  const toggleUserStatus = (id: number) => {
    setUsers(prev =>
      prev.map(user =>
        user.id === id ? { ...user, isActive: !user.isActive } : user
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
          <h2 className="text-2xl font-bold">Gestión de Usuarios y Roles</h2>
          <p className="text-muted-foreground">Administra usuarios, roles y permisos del sistema</p>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Usuarios</p>
                <p className="text-2xl font-bold">{users.length}</p>
              </div>
              <User className="h-5 w-5 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Usuarios Activos</p>
                <p className="text-2xl font-bold text-green-600">
                  {users.filter(u => u.isActive).length}
                </p>
              </div>
              <UserCheck className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Roles</p>
                <p className="text-2xl font-bold">{roles.length}</p>
              </div>
              <Shield className="h-5 w-5 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Roles Activos</p>
                <p className="text-2xl font-bold text-green-600">
                  {roles.filter(r => r.isActive).length}
                </p>
              </div>
              <Shield className="h-5 w-5 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="devices">Equipos</TabsTrigger>
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
              
              <Select value={selectedRole} onValueChange={setSelectedRole}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Filtrar por rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los roles</SelectItem>
                  {roles.map(role => (
                    <SelectItem key={role.id} value={role.id.toString()}>
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
                      <TableHead>Usuario</TableHead>
                      <TableHead>Contacto</TableHead>
                      <TableHead>Rol</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Último Acceso</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">
                              Creado: {new Date(user.createdDate).toLocaleDateString()}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="flex items-center text-sm">
                              <Mail className="h-3 w-3 mr-1" />
                              {user.email}
                            </div>
                            <div className="flex items-center text-sm text-muted-foreground">
                              <Phone className="h-3 w-3 mr-1" />
                              {user.phone}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{user.roleName}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {getStatusBadge(user.isActive)}
                            <Switch
                              checked={user.isActive}
                              onCheckedChange={() => toggleUserStatus(user.id)}
                              disabled={user.id === 1} // No permitir desactivar admin principal
                            />
                          </div>
                        </TableCell>
                        <TableCell>
                          {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Nunca'}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewSessions(user.name)}
                              title="Ver sesiones"
                            >
                              <Activity className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditUser(user)}
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            {user.id !== 1 && ( // No permitir eliminar admin principal
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

        {/* Tab de Roles */}
        <TabsContent value="roles" className="space-y-4">
          <div className="flex justify-end">
            <Button onClick={openAddRoleDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Rol
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {roles.map((role) => (
              <Card key={role.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{role.name}</CardTitle>
                      <CardDescription>{role.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(role.isActive)}
                      <Switch
                        checked={role.isActive}
                        onCheckedChange={() => toggleRoleStatus(role.id)}
                        disabled={role.id === 1} // No permitir desactivar rol de admin
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {role.permissions.length} permisos asignados
                    </p>
                    <div className="text-xs text-muted-foreground">
                      Creado: {new Date(role.createdDate).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditRole(role)}
                      className="flex-1"
                    >
                      <Edit className="h-3 w-3 mr-1" />
                      Editar
                    </Button>
                    {role.id !== 1 && ( // No permitir eliminar rol de admin
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Tab de Equipos */}
        <TabsContent value="devices">
          <DeviceManager />
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
              <Label htmlFor="name">Nombre Completo</Label>
              <Input
                id="name"
                placeholder="Ej: María González"
                value={userFormData.name || ""}
                onChange={(e) => setUserFormData(prev => ({ ...prev, name: e.target.value }))}
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

            <div className="space-y-2">
              <Label htmlFor="phone">Teléfono</Label>
              <Input
                id="phone"
                placeholder="+1234567890"
                value={userFormData.phone || ""}
                onChange={(e) => setUserFormData(prev => ({ ...prev, phone: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="roleId">Rol</Label>
              <Select 
                value={userFormData.roleId?.toString() || ""} 
                onValueChange={(value) => setUserFormData(prev => ({ ...prev, roleId: parseInt(value) }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un rol" />
                </SelectTrigger>
                <SelectContent>
                  {roles.filter(r => r.isActive).map(role => (
                    <SelectItem key={role.id} value={role.id.toString()}>
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
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

      {/* Dialog para Rol */}
      <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingRole ? "Editar Rol" : "Nuevo Rol"}
            </DialogTitle>
            <DialogDescription>
              {editingRole ? "Modifica el rol y sus permisos" : "Crea un nuevo rol con permisos específicos"}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleRoleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="roleName">Nombre del Rol</Label>
                <Input
                  id="roleName"
                  placeholder="Ej: Operador de Turno"
                  value={roleFormData.name || ""}
                  onChange={(e) => setRoleFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="roleDescription">Descripción</Label>
                <Input
                  id="roleDescription"
                  placeholder="Descripción del rol"
                  value={roleFormData.description || ""}
                  onChange={(e) => setRoleFormData(prev => ({ ...prev, description: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="space-y-4">
              <Label className="text-base">Permisos del Rol</Label>
              
              {Object.entries(groupedPermissions).map(([module, permissions]) => (
                <Card key={module}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">{module}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {permissions.map((permission) => (
                        <div key={permission.id} className="flex items-start space-x-2">
                          <Checkbox
                            id={permission.id}
                            checked={(roleFormData.permissions || []).includes(permission.id)}
                            onCheckedChange={(checked) => 
                              handlePermissionToggle(permission.id, checked as boolean)
                            }
                          />
                          <div className="grid gap-1.5 leading-none">
                            <Label
                              htmlFor={permission.id}
                              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                              {permission.name}
                            </Label>
                            <p className="text-xs text-muted-foreground">
                              {permission.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsRoleDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingRole ? "Actualizar" : "Crear Rol"}
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
    </div>
  );
}