import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_BASE_URL } from '../constants';

// Tipos
export interface Permission {
  id_permiso: number;
  modulo: string;
  accion: string;
  descripcion_permiso?: string;
}

export interface Role {
  id_rol: number;
  nombre_rol: string;
  descripcion: string;
  anulado: boolean;
  permisos?: Permission[];
}

export interface UserData {
  email: string;
  nombre: string;
  roles: Role[];
  token: string;
}

interface AuthContextType {
  user: UserData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  hasPermission: (modulo: string, accion?: string) => boolean;
  hasAnyPermission: (modulos: string[]) => boolean;
  hasRole: (roleName: string) => boolean;
  isAdmin: () => boolean;
  canRead: (modulo: string) => boolean;
  canWrite: (modulo: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mapeo de páginas a módulos de permisos
export const PAGE_PERMISSIONS: Record<string, { modulo: string; acciones?: string[] }> = {
  'dashboard': { modulo: 'DASHBOARD' }, // Todos pueden ver el dashboard
  'inventory': { modulo: 'INSUMOS' },
  'recipes': { modulo: 'RECETAS' },
  'purchase-orders': { modulo: 'COMPRAS' },
  'supply-entry': { modulo: 'INVENTARIO' },
  'products': { modulo: 'PRODUCTOS' },
  'suppliers': { modulo: 'PROVEEDORES' },
  'users': { modulo: 'USUARIOS' },
  'alerts': { modulo: 'INVENTARIO' },
  'reports': { modulo: 'REPORTES' },
  'settings': { modulo: 'CONFIGURACION' },
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const savedUser = localStorage.getItem('authUser');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (e) {
        localStorage.removeItem('authUser');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log('📦 Login response:', data);

      if (response.ok && data.success) {
        const loginData = data.data;
        console.log('👤 User roles from login:', loginData.roles);
        
        // Cargar los permisos de cada rol usando el endpoint /roles/{id}
        const rolesWithPermissions = await Promise.all(
          loginData.roles.map(async (role: Role) => {
            try {
              console.log(`🔍 Fetching permissions for role ${role.id_rol} (${role.nombre_rol})`);
              const roleResponse = await fetch(`${API_BASE_URL}/v1/roles/${role.id_rol}`, {
                headers: { 'Content-Type': 'application/json' }
              });
              if (roleResponse.ok) {
                const roleData = await roleResponse.json();
                console.log(`📋 Role ${role.id_rol} data:`, roleData);
                if (roleData.success && roleData.data) {
                  const permisos = roleData.data.lista_permisos || roleData.data.permisos || [];
                  console.log(`✅ Permisos for ${role.nombre_rol}:`, permisos);
                  return { 
                    ...role, 
                    permisos: permisos
                  };
                }
              }
              return { ...role, permisos: [] };
            } catch (err) {
              console.error(`❌ Error fetching role ${role.id_rol}:`, err);
              return { ...role, permisos: [] };
            }
          })
        );

        console.log('🎭 Roles with permissions:', rolesWithPermissions);

        const userData: UserData = {
          email: loginData.email,
          nombre: loginData.nombre,
          roles: rolesWithPermissions,
          token: loginData.token.access_token,
        };

        console.log('💾 Saving user data:', userData);
        setUser(userData);
        localStorage.setItem('authUser', JSON.stringify(userData));
        
        return { success: true };
      } else {
        return { success: false, error: data.message || 'Error en el login' };
      }
    } catch (err) {
      console.error('Error de conexión:', err);
      return { success: false, error: 'Error de conexión con el servidor' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('authUser');
  };

  // Verificar si el usuario es administrador
  const isAdmin = (): boolean => {
    if (!user) return false;
    return user.roles.some(role => 
      role.nombre_rol.toLowerCase() === 'administrador' || 
      role.nombre_rol.toLowerCase() === 'admin'
    );
  };

  // Verificar si tiene un permiso específico
  const hasPermission = (modulo: string, accion?: string): boolean => {
    if (!user) {
      console.log(`🚫 hasPermission(${modulo}): No user`);
      return false;
    }
    
    // Admin tiene todos los permisos
    if (isAdmin()) {
      console.log(`✅ hasPermission(${modulo}): User is admin`);
      return true;
    }

    // Dashboard es accesible para todos los usuarios autenticados
    if (modulo === 'DASHBOARD') return true;

    // Buscar el permiso en todos los roles del usuario
    console.log(`🔍 Checking permission ${modulo} in roles:`, user.roles);
    for (const role of user.roles) {
      if (role.permisos && role.permisos.length > 0) {
        console.log(`📋 Role ${role.nombre_rol} has permisos:`, role.permisos);
        const hasIt = role.permisos.some(perm => {
          // Comparación case-insensitive para modulo y accion
          const moduloMatch = perm.modulo.toUpperCase() === modulo.toUpperCase();
          const accionMatch = accion 
            ? perm.accion.toLowerCase() === accion.toLowerCase()
            : true;
          const match = moduloMatch && accionMatch;
          if (match) console.log(`✅ Found permission: ${perm.modulo} - ${perm.accion}`);
          return match;
        });
        if (hasIt) return true;
      } else {
        console.log(`⚠️ Role ${role.nombre_rol} has no permisos array or is empty`);
      }
    }
    console.log(`❌ Permission ${modulo} not found`);
    return false;
  };

  // Verificar si tiene permiso en al menos uno de los módulos
  const hasAnyPermission = (modulos: string[]): boolean => {
    if (!user) return false;
    if (isAdmin()) return true;
    return modulos.some(modulo => hasPermission(modulo));
  };

  // Verificar si tiene un rol específico
  const hasRole = (roleName: string): boolean => {
    if (!user) return false;
    return user.roles.some(role => 
      role.nombre_rol.toLowerCase() === roleName.toLowerCase()
    );
  };

  // Verificar si puede LEER un módulo (ver)
  const canRead = (modulo: string): boolean => {
    return hasPermission(modulo, 'leer') || hasPermission(modulo, 'escribir');
  };

  // Verificar si puede ESCRIBIR en un módulo (crear, editar, eliminar)
  const canWrite = (modulo: string): boolean => {
    return hasPermission(modulo, 'escribir');
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      hasPermission,
      hasAnyPermission,
      hasRole,
      isAdmin,
      canRead,
      canWrite,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
