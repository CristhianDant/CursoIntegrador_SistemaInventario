import { useState, useEffect } from "react";
import { Plus, Search, Edit, Shield, Mail, Activity } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Checkbox } from "./ui/checkbox";
import { UserSessionModal } from "./UserSessionModal";
import { API_BASE_URL } from "../constants";

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
  es_admin: boolean;
  ultimo_acceso: string | null;
  fecha_registro: string;
  anulado: boolean;
}

export function UserManager() {
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
    const url = editingUser ? `${API_BASE_URL}/v1/usuarios/${editingUser.id_user}` : `${API_BASE_URL}/v1/usuarios/`;
    const method = editingUser ? 'PUT' : 'POST';
    
    const body = editingUser ? {
      id_user: editingUser.id_user,
      nombre: userFormData.nombre,
      apellidos: userFormData.apellidos,
      email: userFormData.email,
    } : {
      nombre: userFormData.nombre,
      apellidos: userFormData.apellidos,
      email: userFormData.email,
      password: userFormData.password
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        await fetchUsers();
        setIsUserDialogOpen(false);
        setEditingUser(null);
        setUserFormData({});
      } else console.error('Error al guardar usuario:', await response.text());
    } catch (error) { console.error('Error de conexión al guardar usuario:', error); }
  };

  const handleRoleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingRole ? `${API_BASE_URL}/v1/roles/${editingRole.id_rol}` : `${API_BASE_URL}/v1/roles/`;
    const method = editingRole ? 'PUT' : 'POST';
    
    const body = editingRole ? {
        id_rol: editingRole.id_rol,
        nombre_rol: roleFormData.nombre_rol,
        descripcion: roleFormData.descripcion,
        lista_permisos: [] // TODO: Implementar asignación de permisos a roles
    } : {
        nombre_rol: roleFormData.nombre_rol,
        descripcion: roleFormData.descripcion,
        lista_permisos: [] // TODO: Implementar asignación de permisos a roles
    };

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        await fetchRoles();
        setIsRoleDialogOpen(false);
        setEditingRole(null);
        setRoleFormData({ nombre_rol: '', descripcion: '' });
      } else console.error('Error al guardar rol:', await response.text());
    } catch (error) { console.error('Error de conexión al guardar rol:', error); }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormData(user);
    setIsUserDialogOpen(true);
  };

  const handleEditRole = (role: Role) => {
    setEditingRole(role);
    setRoleFormData({ nombre_rol: role.nombre_rol, descripcion: role.descripcion });
    setIsRoleDialogOpen(true);
  };

  const openAddUserDialog = () => {
    setEditingUser(null);
    setUserFormData({});
    setIsUserDialogOpen(true);
  };

  const openAddRoleDialog = () => {
    setEditingRole(null);
    setRoleFormData({ nombre_rol: '', descripcion: '' });
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
            <Button onClick={openAddUserDialog}><Plus className="h-4 w-4 mr-2" />Nuevo Usuario</Button>
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
                    <TableHead>Admin</TableHead>
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
                      <TableCell><Badge variant={user.es_admin ? "default" : "secondary"}>{user.es_admin ? "Sí" : "No"}</Badge></TableCell>
                      <TableCell>{user.ultimo_acceso ? new Date(user.ultimo_acceso).toLocaleDateString() : 'Nunca'}</TableCell>
                      <TableCell><Badge variant={user.anulado ? "destructive" : "outline"}>{user.anulado ? "Anulado" : "Activo"}</Badge></TableCell>
                      <TableCell className="text-right">
                        <div className="flex space-x-2 justify-end">
                          <Button variant="outline" size="icon" onClick={() => handleViewSessions(user.nombre)} title="Ver sesiones"><Activity className="h-4 w-4" /></Button>
                          <Button variant="outline" size="icon" onClick={() => handleManagePermissions(user)} title="Gestionar permisos"><Shield className="h-4 w-4" /></Button>
                          <Button variant="outline" size="icon" onClick={() => handleEditUser(user)} title="Editar usuario"><Edit className="h-4 w-4" /></Button>
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
            <Button onClick={openAddRoleDialog}><Plus className="h-4 w-4 mr-2" />Nuevo Rol</Button>
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
                          <Button variant="outline" size="icon" title="Asignar permisos al rol (Próximamente)"><Shield className="h-4 w-4" /></Button>
                          <Button variant="outline" size="icon" onClick={() => handleEditRole(role)} title="Editar rol"><Edit className="h-4 w-4" /></Button>
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
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingUser ? "Editar Usuario" : "Nuevo Usuario"}</DialogTitle>
            <DialogDescription>{editingUser ? "Modifica la información del usuario." : "Crea un nuevo usuario para el sistema."}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUserSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nombre">Nombre</Label>
              <Input id="nombre" placeholder="Ej: Ana" value={userFormData.nombre || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, nombre: e.target.value }))} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="apellidos">Apellidos</Label>
              <Input id="apellidos" placeholder="Ej: García" value={userFormData.apellidos || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, apellidos: e.target.value }))} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico</Label>
              <Input id="email" type="email" placeholder="usuario@sweetstock.com" value={userFormData.email || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, email: e.target.value }))} required />
            </div>
            {!editingUser && (
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input id="password" type="password" placeholder="Contraseña segura" value={userFormData.password || ""} onChange={(e) => setUserFormData(prev => ({ ...prev, password: e.target.value }))} required />
              </div>
            )}
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsUserDialogOpen(false)}>Cancelar</Button>
              <Button type="submit">{editingUser ? "Actualizar" : "Crear Usuario"}</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingRole ? "Editar Rol" : "Nuevo Rol"}</DialogTitle>
            <DialogDescription>{editingRole ? "Modifica la información del rol." : "Crea un nuevo rol para asignar a los usuarios."}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleRoleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nombre_rol">Nombre del Rol</Label>
              <Input id="nombre_rol" placeholder="Ej: Gerente de Producción" value={roleFormData.nombre_rol || ""} onChange={(e) => setRoleFormData(prev => ({ ...prev, nombre_rol: e.target.value }))} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="descripcion_rol">Descripción</Label>
              <Input id="descripcion_rol" placeholder="Ej: Responsable de la línea de producción" value={roleFormData.descripcion || ""} onChange={(e) => setRoleFormData(prev => ({ ...prev, descripcion: e.target.value }))} required />
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